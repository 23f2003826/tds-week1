# Question 9: Portfolio on GitHub Pages

Publish a modern portfolio page using **GitHub Pages** that showcases your technical work, ensuring your email address is rendered with Cloudflare obfuscation bypass tags.

---

## 📋 Requirements

* **Target URL Format**: `https://<USER>.github.io/<REPO>/`
  * Your URL: `https://23f2003826.github.io/tds-week1/`
* **Email Safeguard**:
  * Cloudflare obfuscates plain email addresses on GitHub Pages.
  * Must be wrapped in:
    ```html
    <!--email_off-->23f2003826@ds.study.iitm.ac.in<!--/email_off-->
    ```
* **Portfolio Showcase**:
  * Contains details of Week 1 assignments and projects.

---

## ⚙️ Enabling GitHub Pages (One-Time Setup)

1. Open your repository on GitHub:
   ```text
   https://github.com/23f2003826/tds-week1
   ```
2. Click **Settings** (top navigation bar) $\to$ **Pages** (in the left sidebar under *Code and automation*).
3. Under **Build and deployment**:
   * **Source**: `Deploy from a branch`
   * **Branch**: `main`
   * **Folder**: `/ (root)`
4. Click **Save**.
5. Wait ~30–60 seconds for GitHub Actions to build and deploy.

---

## 🔑 Your GitHub Pages URL to Submit

```text
https://23f2003826.github.io/tds-week1/
```

*(If testing immediately after deployment and changes aren't reflected, add a cache buster like `https://23f2003826.github.io/tds-week1/?v=1`)*

