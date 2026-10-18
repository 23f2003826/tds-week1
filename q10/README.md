# Question 10: Git Forensics - Recover Leaked Staging Token

Rebuilding a repository from a `git fast-import` stream and using git history forensics to recover a leaked staging token and identify the commit that introduced it.

---

## 📋 Task Details

* **Input File**: `q10/history.fastimport`
* **Target File in History**: `config/app.env`
* **Forensics Goal**:
  1. Rebuild repository using `git fast-import`.
  2. Pinpoint the commit that introduced the `STAGING_TOKEN`.
  3. Extract the original token and commit subject line.

---

## 🔍 Investigation Steps

```bash
# 1. Initialize and rebuild repository
mkdir repo && cd repo && git init -q
git fast-import --quiet < ../history.fastimport
git checkout -f main

# 2. Pinpoint commit modifying STAGING_TOKEN
git log -S 'STAGING_TOKEN=' --oneline -- config/app.env
# Output: 5e43fb5 Add staging deploy token to app config

# 3. View the diff of the introducing commit
git show 5e43fb5 -- config/app.env
```

### Git Diff Output:
```diff
commit 5e43fb544f2b2d4f8e52cccd6c72bcef69e0d226
Author: CI Bot <ci@example.com>
Date:   Mon May 6 17:53:20 2024 +0000

    Add staging deploy token to app config

diff --git a/config/app.env b/config/app.env
index 2d6571d..cf468ed 100644
--- a/config/app.env
+++ b/config/app.env
@@ -1,3 +1,4 @@
 APP_ENV=staging
 LOG_LEVEL=info
+STAGING_TOKEN=stg_6d77f1c49cbada904a776e23
 FEATURE_CACHE=true
```

---

## 🔑 Recovered Values

* **Leaked Token**: `stg_6d77f1c49cbada904a776e23`
* **Commit Subject**: `Add staging deploy token to app config`

---

## 📤 Submission JSON

```json
{
  "token": "stg_6d77f1c49cbada904a776e23",
  "commit_subject": "Add staging deploy token to app config"
}
```
