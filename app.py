"""
🌌 CosmoBlog — Flask Blog Application
A full-featured blog with authentication, admin panel,
categories, comments, and rich article management.
"""

from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, abort, jsonify)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import re

# ── App Setup ──────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY']          = os.environ.get('SECRET_KEY', 'cosmo-blog-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Models ─────────────────────────────────────────────────

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    posts         = db.relationship('Post', backref='author', lazy=True)
    comments      = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, pw):   self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)


class Category(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(50), unique=True, nullable=False)
    slug  = db.Column(db.String(60), unique=True, nullable=False)
    color = db.Column(db.String(20), default='#6C63FF')
    posts = db.relationship('Post', backref='category', lazy=True)


class Post(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    slug        = db.Column(db.String(220), unique=True, nullable=False)
    excerpt     = db.Column(db.String(300))
    content     = db.Column(db.Text, nullable=False)
    cover_emoji = db.Column(db.String(10), default='🌌')
    published   = db.Column(db.Boolean, default=False)
    views       = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    comments    = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    body       = db.Column(db.Text, nullable=False)
    approved   = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


# ── Helpers ────────────────────────────────────────────────

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)[:200]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

app.jinja_env.globals['current_user'] = current_user
app.jinja_env.globals['now'] = datetime.utcnow


# ── Public Routes ──────────────────────────────────────────

@app.route('/')
def index():
    page     = request.args.get('page', 1, type=int)
    cat_slug = request.args.get('category')
    search   = request.args.get('q', '').strip()

    query = Post.query.filter_by(published=True)

    if cat_slug:
        cat   = Category.query.filter_by(slug=cat_slug).first_or_404()
        query = query.filter_by(category_id=cat.id)
    else:
        cat = None

    if search:
        query = query.filter(
            Post.title.ilike(f'%{search}%') | Post.content.ilike(f'%{search}%')
        )

    posts      = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6)
    categories = Category.query.all()
    featured   = Post.query.filter_by(published=True).order_by(Post.views.desc()).first()
    recent     = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).limit(3).all()

    return render_template('index.html',
        posts=posts, categories=categories,
        featured=featured, recent=recent,
        active_cat=cat, search=search)


@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    post.views += 1
    db.session.commit()
    comments   = Comment.query.filter_by(post_id=post.id, approved=True).order_by(Comment.created_at).all()
    related    = Post.query.filter(
        Post.category_id == post.category_id,
        Post.id != post.id,
        Post.published == True
    ).limit(3).all()
    return render_template('post_detail.html', post=post, comments=comments, related=related)


@app.route('/post/<slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    body = request.form.get('body', '').strip()
    if not body:
        flash('Comment cannot be empty.', 'error')
    else:
        comment = Comment(body=body, user_id=session['user_id'], post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
    return redirect(url_for('post_detail', slug=slug))


@app.route('/category/<slug>')
def category(slug):
    return redirect(url_for('index', category=slug))


# ── Auth Routes ────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash(f'Welcome, {username}! 🌌', 'success')
            return redirect(url_for('index'))

    return render_template('auth.html', mode='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user     = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}! 🚀', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.', 'error')

    return render_template('auth.html', mode='login')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ── Admin Routes ───────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'posts':    Post.query.count(),
        'users':    User.query.count(),
        'comments': Comment.query.count(),
        'views':    db.session.query(db.func.sum(Post.views)).scalar() or 0,
    }
    recent_posts    = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
        stats=stats, recent_posts=recent_posts, recent_comments=recent_comments)


@app.route('/admin/posts')
@admin_required
def admin_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)


@app.route('/admin/posts/new', methods=['GET', 'POST'])
@admin_required
def admin_new_post():
    categories = Category.query.all()
    if request.method == 'POST':
        title    = request.form['title'].strip()
        content  = request.form['content'].strip()
        excerpt  = request.form.get('excerpt', '').strip()
        emoji    = request.form.get('cover_emoji', '🌌').strip() or '🌌'
        cat_id   = request.form.get('category_id') or None
        publish  = 'publish' in request.form

        slug = slugify(title)
        # ensure unique slug
        base, n = slug, 1
        while Post.query.filter_by(slug=slug).first():
            slug = f'{base}-{n}'; n += 1

        post = Post(title=title, slug=slug, content=content,
                    excerpt=excerpt, cover_emoji=emoji,
                    category_id=cat_id, published=publish,
                    user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('admin_posts'))

    return render_template('admin/post_form.html', post=None, categories=categories)


@app.route('/admin/posts/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_post(id):
    post       = Post.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        post.title       = request.form['title'].strip()
        post.content     = request.form['content'].strip()
        post.excerpt     = request.form.get('excerpt', '').strip()
        post.cover_emoji = request.form.get('cover_emoji', '🌌').strip() or '🌌'
        post.category_id = request.form.get('category_id') or None
        post.published   = 'publish' in request.form
        post.updated_at  = datetime.utcnow()
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('admin_posts'))

    return render_template('admin/post_form.html', post=post, categories=categories)


@app.route('/admin/posts/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('admin_posts'))


@app.route('/admin/posts/<int:id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_post(id):
    post           = Post.query.get_or_404(id)
    post.published = not post.published
    db.session.commit()
    return jsonify({'published': post.published})


@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    if request.method == 'POST':
        name  = request.form['name'].strip()
        color = request.form.get('color', '#6C63FF')
        slug  = slugify(name)
        if not Category.query.filter_by(slug=slug).first():
            cat = Category(name=name, slug=slug, color=color)
            db.session.add(cat)
            db.session.commit()
            flash('Category added!', 'success')
        else:
            flash('Category already exists.', 'error')
        return redirect(url_for('admin_categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('admin_categories'))


@app.route('/admin/comments')
@admin_required
def admin_comments():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)


@app.route('/admin/comments/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('admin_comments'))


@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/<int:id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(id):
    user = User.query.get_or_404(id)
    if user.id != session['user_id']:
        user.is_admin = not user.is_admin
        db.session.commit()
    return redirect(url_for('admin_users'))


# ── Error Handlers ─────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, msg='Access Forbidden'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, msg='Page Not Found'), 404


# ── Seed Data ──────────────────────────────────────────────

def seed_db():
    """Create default admin, categories, and sample posts."""
    if User.query.first():
        return

    # Admin user
    admin = User(username='admin', email='admin@cosmo.blog', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)

    # Categories
    cats_data = [
        ('Technology', 'technology', '#6C63FF'),
        ('Science',    'science',    '#00D2FF'),
        ('Space',      'space',      '#FF6B6B'),
        ('Lifestyle',  'lifestyle',  '#43E97B'),
        ('Travel',     'travel',     '#F7971E'),
    ]
    cats = {}
    for name, slug, color in cats_data:
        c = Category(name=name, slug=slug, color=color)
        db.session.add(c)
        cats[slug] = c

    db.session.flush()

    # Sample posts
    posts_data = [
        ('The Future of Artificial Intelligence',
         'space',
         '🤖',
         'Exploring how AI is reshaping industries and what it means for humanity\'s future.',
         '''Artificial intelligence is no longer a distant dream — it's the engine driving the modern world. From recommendation systems that know what you'll watch next, to language models that can write code, diagnose diseases, and compose music, AI has permeated every corner of our lives.

The question is no longer *whether* AI will transform the world, but *how fast* and *at what cost*.

## The Current Landscape

Today's AI systems are built primarily on transformer architectures — neural networks trained on vast datasets. GPT-4, Gemini, Claude, and their successors demonstrate that scale and data unlock emergent capabilities that their creators didn't explicitly program.

These models can now:
- Write and debug code across dozens of languages
- Summarize legal documents with high accuracy
- Generate photorealistic images from text descriptions
- Engage in nuanced multi-turn conversations

## What's Coming Next

Researchers believe we're approaching a threshold where AI systems can autonomously plan and execute complex tasks. This is called *agentic AI* — AI that doesn't just respond, but acts.

Autonomous agents will soon be able to browse the web, write and run code, manage calendars, and coordinate with other agents to complete week-long projects overnight.

## The Human Question

The deeper question isn't technical — it's philosophical. As AI grows more capable, society must decide: what roles do we *want* humans to play? What work is inherently human? What decisions should never be delegated to an algorithm?

These aren't questions AI can answer for us. They require the one thing AI doesn't have: lived human experience and genuine stake in the outcome.'''),

        ('Black Holes: Nature\'s Most Extreme Objects',
         'space',
         '🕳️',
         'A deep dive into black holes — what they are, how they form, and why they matter.',
         '''Black holes are the universe's ultimate extremists. They are regions of spacetime where gravity is so strong that nothing — not even light — can escape. They are born from the deaths of massive stars and grow by consuming everything around them.

## How Black Holes Form

When a star more than 20 times the mass of our Sun exhausts its nuclear fuel, it can no longer support itself against its own gravity. The core collapses in milliseconds, then rebounds in a catastrophic supernova explosion. What remains — if the star was massive enough — is a black hole.

The boundary of no return is called the **event horizon**. Cross it, and the laws of physics as we understand them break down.

## The Singularity Problem

At the center of a black hole lies a *singularity* — a point of infinite density where our mathematical models of physics produce nonsensical answers. This is a sign, physicists believe, that general relativity is incomplete. A full theory of quantum gravity is needed to describe what truly happens inside.

## Supermassive Black Holes

Every large galaxy, including our Milky Way, harbors a supermassive black hole at its center. The Milky Way's — called Sagittarius A* — has the mass of 4 million Suns. The largest known black holes exceed 40 billion solar masses.

In 2019, humanity captured its first image of a black hole. In 2022, we photographed our own galactic center. These images confirmed predictions made over a century ago by Einstein's equations.

Black holes remain the most extreme laboratories in nature — and our best chance at understanding the deepest laws of the cosmos.'''),

        ('10 Python Tips Every Developer Should Know',
         'technology',
         '🐍',
         'Level up your Python skills with these practical tips and tricks.',
         '''Python's simplicity is deceptive. Its clean syntax hides a remarkably deep language with powerful features that even experienced developers overlook. Here are ten techniques that will make your code cleaner, faster, and more Pythonic.

## 1. Use f-strings for Formatting

Instead of `"Hello, " + name`, write `f"Hello, {name}"`. f-strings are faster, cleaner, and support expressions: `f"Price: {price * 1.2:.2f}"`.

## 2. Enumerate Instead of Range

```python
# Instead of:
for i in range(len(items)):
    print(i, items[i])

# Use:
for i, item in enumerate(items):
    print(i, item)
```

## 3. List Comprehensions

```python
squares = [x**2 for x in range(10) if x % 2 == 0]
```

Concise, readable, and faster than a for loop for simple transformations.

## 4. The Walrus Operator

Python 3.8+ introduced `:=` for assignment expressions:

```python
while chunk := file.read(8192):
    process(chunk)
```

## 5. Dataclasses for Clean Models

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"
```

Auto-generates `__init__`, `__repr__`, and `__eq__`.

## 6. Context Managers

Always use `with` for file and database operations. It guarantees cleanup even on exceptions.

## 7. defaultdict and Counter

```python
from collections import Counter
words = ["hello", "world", "hello"]
print(Counter(words))  # Counter({'hello': 2, 'world': 1})
```

## 8. Generator Expressions

For large datasets, use generators instead of lists to save memory:

```python
total = sum(x**2 for x in range(1_000_000))
```

## 9. Unpacking

```python
first, *rest = [1, 2, 3, 4, 5]
a, b = b, a  # swap!
```

## 10. Type Hints

```python
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()
```

Type hints make code self-documenting and enable better IDE support and static analysis.'''),
    ]

    db.session.flush()
    for title, cat_slug, emoji, excerpt, content in posts_data:
        slug = slugify(title)
        p = Post(title=title, slug=slug, excerpt=excerpt,
                 content=content, cover_emoji=emoji,
                 category_id=cats[cat_slug].id,
                 published=True, views=0, user_id=admin.id)
        db.session.add(p)

    db.session.commit()
    print("✅ Database seeded with admin, categories, and sample posts.")


# ── Run ────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
