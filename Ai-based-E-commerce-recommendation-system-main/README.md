# 🛍️ AI Store - Project Setup Guide

This guide will help you **run the AI Store project locally** on your system step-by-step.

---

## 📌 Step 1: Clone or Download the Project

### Option 1: Using Git

```bash
git clone https://github.com/Sanjaykris20/AI-Store.git
cd AI-Store
```

### Option 2: Download ZIP

* Click **Code → Download ZIP**
* Extract the folder
* Open it in **VS Code**

---

## 📌 Step 2: Identify Project Type

Check the files in the project folder:

| File Found         | Project Type         |
| ------------------ | -------------------- |
| `index.html`       | Static Website       |
| `package.json`     | React / Node Project |
| `requirements.txt` | Python Backend       |

---

## 🚀 Step 3: Run the Project

---

### ✅ Case 1: Static Website (index.html)

#### Method 1 (Simple)

* Open `index.html` in your browser

#### Method 2 (Recommended)

* Install **Live Server extension in VS Code**
* Right-click `index.html`
* Click **Open with Live Server**

👉 Runs on:
http://127.0.0.1:5500

---

### ✅ Case 2: React / Node Project

#### Step 1: Install Node.js

Download and install Node.js if not already installed.

#### Step 2: Install Dependencies

```bash
npm install
```

#### Step 3: Start the Project

```bash
npm start
```

👉 Open in browser:
http://localhost:3000

---

### ✅ Case 3: Python Backend (if applicable)

#### Install dependencies:

```bash
pip install -r requirements.txt
```

#### Run backend:

```bash
python app.py
```

---

## ⚠️ Common Errors & Fixes

### ❌ npm not recognized

👉 Install Node.js

---

### ❌ Module not found

```bash
npm install
```

---

### ❌ Port already in use

```bash
npm start -- --port 3001
```

---

### ❌ Blank Page / Not Loading

* Open browser console (F12)
* Check for errors
* Verify file paths

---

## 🧪 Final Check

Make sure:

* Website loads correctly
* UI is visible
* Buttons and features work
* No console errors

---

## 🎯 Summary

| Step | Action                   |
| ---- | ------------------------ |
| 1    | Clone / Download project |
| 2    | Identify project type    |
| 3    | Run using correct method |
| 4    | Fix errors if any        |

---

## 🚀 You're Ready!

Your AI Store project should now be running locally 🎉

---

💡 If you face any issues, check errors carefully or debug step-by-step.
