# 🌌 CosmoBlog — Full-Stack Python Blog Application

> *"Where ideas orbit the mind."*

A fully-featured blog web application built with **Python + Flask** as an internship project demonstrating full-stack development skills including authentication, database management, admin panel, and dynamic content rendering.

---

## 🌐 Live Demo

👉 **[View Live App](https://cosmo-blog.onrender.com)**
*(Replace with your Render URL after deploying)*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **User Authentication** | Register, login, logout with password hashing (Werkzeug) |
| 📝 **Blog Posts** | Create, edit, delete, publish/draft with rich content |
| 🏷 **Categories** | Color-coded category system with filter navigation |
| 💬 **Comments** | Authenticated users can comment on any post |
| ⚙️ **Admin Panel** | Full dashboard with stats, post management, user control |
| 🔍 **Search** | Full-text search across post titles and content |
| 📄 **Pagination** | Posts paginated at 6 per page |
| 📊 **View Tracking** | Automatic view count per post |
| 🌌 **Space Theme** | Dark cosmos UI with animated stars and gradient accents |
| 📱 **Responsive** | Mobile-first design, works on all screen sizes |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **Framework** | Flask 3.0 |
| **Database ORM** | Flask-SQLAlchemy |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | Werkzeug password hashing + Flask sessions |
| **Templates** | Jinja2 (Flask templating engine) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Fonts** | Google Fonts — Space Grotesk + Space Mono |
| **Server** | Gunicorn (production) |
| **Hosting** | Render (free tier) |

---

## 📁 Project Structure

```
cosmos-blog/
│
├── app.py                   ← Main Flask app (routes, models, logic)
├── requirements.txt         ← Python dependencies
├── Procfile                 ← Production server command
├── .gitignore               ← Files to exclude from Git
├── README.md                ← This file
│
├── templates/               ← Jinja2 HTML templates
│   ├── base.html            ← Shared layout (navbar, footer, flash)
│   ├── index.html           ← Homepage with posts grid + featured
│   ├── post_detail.html     ← Individual post + comments
│   ├── auth.html            ← Login / Register form
│   ├── error.html           ← 403 / 404 error pages
│   │
│   └── admin/               ← Admin panel templates
│       ├── base.html        ← Admin sidebar layout
│       ├── dashboard.html   ← Stats + recent activity
│       ├── posts.html       ← All posts table
│       ├── post_form.html   ← Create / Edit post form
│       ├── categories.html  ← Category management
│       ├── comments.html    ← Comment moderation
│       └── users.html       ← User management
│
└── static/                  ← CSS and JS files
    ├── css/
    │   ├── style.css        ← Main space theme stylesheet
    │   └── admin.css        ← Admin panel styles
    └── js/
        └── main.js          ← Client-side JavaScript
```

---

## 🗄 Database Models

```
User         ← id, username, email, password_hash, is_admin, created_at
Category     ← id, name, slug, color
Post         ← id, title, slug, excerpt, content, cover_emoji, published, views, created_at, user_id, category_id
Comment      ← id, body, approved, created_at, user_id, post_id
```

---

## 🚀 Run Locally

### Step 1 — Install Python 3.8+
Download from [python.org](https://python.org) if you don't have it.
```bash
python --version  # should show 3.8 or higher
```

### Step 2 — Clone or download the project
```bash
git clone https://github.com/YOUR-USERNAME/cosmos-blog.git
cd cosmos-blog
```

### Step 3 — Create a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run the app
```bash
python app.py
```

### Step 6 — Open in browser
Go to 👉 **http://localhost:5000**

The database is created automatically with seed data:
- **Admin login:** `admin` / `admin123`
- 3 sample blog posts
- 5 categories (Technology, Science, Space, Lifestyle, Travel)

---

## ☁️ Deploy on Render (Free Live Link)

### Step 1 — Push to GitHub

1. Go to **github.com** → Sign Up (free)
2. Click **New Repository** → name it `cosmos-blog` → **Public** → Create
3. Click **"uploading an existing file"**
4. Upload files **in this order**:

   **First, upload these files (drag all at once):**
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `.gitignore`
   - `README.md`

   Click **Commit changes**.

   **Then upload the folders one by one:**

   For `templates/` folder:
   - Click **Add file → Create new file**
   - Type `templates/base.html` → paste contents → Commit
   - Repeat for every file inside `templates/` and `templates/admin/`

   For `static/` folder:
   - Click **Add file → Create new file**
   - Type `static/css/style.css` → paste contents → Commit
   - Type `static/css/admin.css` → paste contents → Commit
   - Type `static/js/main.js` → paste contents → Commit

> **Tip:** If you have Git installed locally, it's much faster to use:
> ```bash
> git init
> git add .
> git commit -m "🌌 Initial commit - CosmoBlog"
> git remote add origin https://github.com/YOUR-USERNAME/cosmos-blog.git
> git push -u origin main
> ```

### Step 2 — Deploy on Render

1. Go to **render.com** → Sign Up with GitHub (free)
2. Click **New + → Web Service**
3. Select **Connect a repository** → choose `cosmos-blog`
4. Fill in settings:

| Setting | Value |
|---------|-------|
| Name | `cosmos-blog` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Plan | Free |

5. Click **Create Web Service**
6. Wait 3–5 minutes for the build to finish
7. Your live URL appears at the top of the page:

```
https://cosmos-blog.onrender.com
```

---

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

> **Change the admin password** immediately after deploying in production.

---

## 🛡 Security Features

- Passwords hashed with Werkzeug's `generate_password_hash` (PBKDF2-HMAC-SHA256)
- Session-based authentication with secret key
- `@login_required` and `@admin_required` decorators protect all sensitive routes
- CSRF protection via form POST methods
- SQL injection prevented via SQLAlchemy ORM

---

## 📸 Pages Overview

| URL | Page |
|-----|------|
| `/` | Homepage with featured post + post grid |
| `/post/<slug>` | Full article with comments |
| `/login` | Login form |
| `/register` | Registration form |
| `/admin` | Admin dashboard (admin only) |
| `/admin/posts` | Manage all posts |
| `/admin/posts/new` | Create new post |
| `/admin/categories` | Manage categories |
| `/admin/comments` | Moderate comments |
| `/admin/users` | Manage users |

---

## 📜 License

MIT License — free to use, modify, and submit as your internship project.

---

## 👤 Author

Built as **Project 6 — Blog Website** for a Python Developer Internship.
Crafted with ☕, Python, and a love for the cosmos. 🌌
