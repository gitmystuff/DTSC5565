# GitHub Pages: Publishing Your About Me Page
### A Follow-Along Guide

This week: publish a small "About Me" page as a **project site** on GitHub Pages. Later in the course, we'll cover converting this pattern into your **personal site** (`<username>.github.io`) and connecting a custom domain.

---

## Step 1 — Create a new repository

1. Go to **github.com**, click the **+** (top right) → **New repository**
2. Name it something like `about-me` or `portfolio` (any name is fine — this is a *project* site, not the special personal-site repo)
3. Set it to **Public** (GitHub Pages on the free tier requires a public repo, unless you're on GitHub Pro/Team)
4. Check **Add a README file**
5. Click **Create repository**

---

## Step 2 — Add your files

You should have two files from your generated page: `index.html` and `style.css`.

1. In your new repo, click **Add file → Upload files**
2. Drag in `index.html` and `style.css`
3. Scroll down, write a short commit message (e.g., "Add About Me page"), and click **Commit changes**

*(If you're comfortable with Git locally or in Colab, `git add`, `git commit`, and `git push` work the same way — the web upload is just the fastest path for today.)*

---

## Step 3 — Enable GitHub Pages

1. In your repo, click **Settings**
2. In the left sidebar, click **Pages**
3. Under **Build and deployment → Source**, choose **Deploy from a branch**
4. Under **Branch**, select **main** and folder **/ (root)** — since `index.html` is at the top level of the repo
5. Click **Save**

---

## Step 4 — Find and verify your live URL

1. Still in **Settings → Pages**, GitHub will show a message like:
   *"Your site is live at `https://<your-username>.github.io/<repo-name>/`"*
2. It can take **1-2 minutes** the first time — refresh if it's not up yet
3. Visit the URL and confirm:
   - [ ] Your name and bio appear correctly
   - [ ] Your interests/skills section is there
   - [ ] Your contact info/links work
   - [ ] The page looks reasonable on your phone too (resize your browser window narrow, or actually check on your phone)
   - [ ] No leftover placeholder text (like "Lorem ipsum" or "[your name here]")

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Page shows a 404 | Wait a minute and refresh — first deploy takes a moment. Also double-check the branch/folder setting in Step 3. |
| Styling isn't showing up | Check that `style.css` is in the same folder as `index.html`, and that `index.html` links to it correctly: `<link rel="stylesheet" href="style.css">` |
| Changes aren't showing | GitHub Pages can take a minute or two to redeploy after each commit — check the **Actions** tab in your repo to see if the deployment finished |

---

## Coming Later in the Course: Your Personal Site & Custom Domain

What you built today is a **project site** — it lives at `<username>.github.io/<repo-name>/`. Later, we'll walk through two upgrades:

**1. The personal/user site**
GitHub gives every account one special repository name: `<username>.github.io`. A repo with *exactly* that name (and nothing else) gets served at the root of your GitHub Pages domain — `https://<username>.github.io/`, no repo name in the path. This becomes your permanent portfolio home, and project sites (like this week's) can be linked into it.

**2. A custom domain**
Once you have a personal site, you can point a domain you own (e.g., `yourname.dev`) at it instead of using the `github.io` address. That involves:
- Adding a `CNAME` file to your repo with your domain name
- Creating **A records** (and/or a `CNAME` record for a `www` subdomain) at your domain registrar, pointing to GitHub's servers
- Waiting for DNS to propagate (can take anywhere from minutes to ~24-48 hours)

We'll walk through both of these step by step when we get there — no need to worry about them yet.
