# Pole Guy Wire Mechanical Calculator

A specialized engineering web application designed to calculate mechanical equilibrium, cable tensions, safety factors, anchor loads, and compressive pole thrust for utility poles according to **PEA / TIS 404 / ASTM** standards. Default presets are configured for a **22-meter transmission/subtransmission pole**.

---

## Features

- **Multi-Level Guy Wire Balancing (Elastic Method)**:
  - Supports an arbitrary number of guy wire levels (dynamically add/remove via `+ Add Guy`).
  - Per-level guy wire sizing (25, 35, 50, and 95 sq.mm steel strand) with exact 100% moment equilibrium.
  - Automatic safety factor evaluation ($SF \ge 2.0$: Safe, $1.5 \le SF < 2.0$: Caution, $SF < 1.5$: Overloaded).
- **Multi-Level Phase Conductors & OHGW (Shield Wire)**:
  - Supports an arbitrary number of conductor levels (dynamically add/remove via `+ Add Conductor`).
  - Conductor catenary tension calculation using resultant unit weight due to wind:
    $$w_r = \sqrt{w^2 + w_{wind}^2}$$
  - Overhead Ground Wire (OHGW) mounted over top conductor C1.
  - Bundled conductor support (1 to 10 conductors per phase).
  - Quick toolbar to batch-apply span, sag, wind pressure, and bundle quantity.
- **Conductor Database (SQLite)**:
  - 25+ pre-seeded standard conductors (ACSR, AAC, SAC).
  - In-app SQL database manager modal for browsing, searching, adding, editing, and resetting conductors.
- **Interactive 2D Visualization**:
  - Real-time SVG rendering of the pole, embedment, anchor line, guy wires, crossarms, conductors, and force vectors.
- **Reporting & Print Export**:
  - Formatted print stylesheet for engineering reports.

---

## Local Setup & Running

### Requirements
- Python 3.9+
- pip

### Quick Start (Windows)
Double-click `run.bat` or run:

```powershell
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Open your browser at **http://127.0.0.1:5000**.

### Running Tests
```powershell
python -m unittest discover tests
```

---

## Deploying on Vercel

The application is pre-configured for instant deployment on [Vercel](https://vercel.com) as a serverless Python Flask application.

### Method 1: Deploy via GitHub (Recommended)

1. Push your repository to **GitHub** (or GitLab/Bitbucket):
   ```bash
   git add .
   git commit -m "Configure Vercel deployment"
   git push origin main
   ```
2. Go to the [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Vercel automatically detects the Python project and configuration (`vercel.json`, `api/index.py`, `requirements.txt`).
5. Click **"Deploy"**. Your app will be live within seconds!

---

### Method 2: Deploy via Vercel CLI

1. Install the Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```
2. Log in to Vercel:
   ```bash
   vercel login
   ```
3. Deploy directly from the project directory:
   ```bash
   vercel
   ```
   For production deployment:
   ```bash
   vercel --prod
   ```

---

## How Serverless on Vercel Works

- **Entry Point (`api/index.py`)**:
  Vercel routes all requests (`/(.*)`) to `api/index.py` via `vercel.json`. The Flask `app` WSGI instance is loaded and invoked by `@vercel/python`.
- **Static Assets (`/static/...`)**:
  Flask serves stylesheets, client-side calculator mechanics, visualizer, and UI scripts from the `static/` directory with explicit paths.
- **SQLite Database (`/tmp/conductors.db`)**:
  On Vercel, the application files in `/var/task` reside on a read-only filesystem. `database/db.py` automatically detects the Vercel serverless environment (`VERCEL=1`) and initializes the database in `/tmp/conductors.db` using the bundled seed data, allowing complete read/write/reset operations without read-only filesystem errors.
