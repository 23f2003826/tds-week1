# Question 7: File Archive Reorganization

Reorganizing a legacy file archive by extracting categories from text files, flattening nested paths into hyphenated file names, and grouping them into category folders.

---

## 🛠️ The Challenge

* **Source Archive**: 30 `.txt` files scattered across deep nested directories (`project/`, `archive/`, `content/`, `docs/`).
* **Path Characteristics**:
  * Spaces in folder names (e.g., `archive/part 2/`)
  * Unicode characters & accents (e.g., `café-2024`, `módulo-3`, `références`, `naïve`)
  * Non-ASCII category names (e.g., `café`, `résumé`, `日本語`)
  * Windows CRLF line endings in some text files.

---

## 📋 Reorganization Rules

1. **Category Extraction**:
   * Read the **first line** matching `^category:`.
   * Extract category value (e.g. `category: resources` $\to$ `resources`).
2. **Directory Creation**:
   * Create folder for each category (e.g., `mkdir -p "$category"`).
3. **Path-to-Dashes Transformation**:
   * Convert relative path `a/b/c/file.txt` $\to$ `a-b-c-file.txt`.
   * Move file to `{category}/{new-name}`.
4. **Clean up**:
   * Delete empty directories.
5. **Verification Hash**:
   * Run `find . -type f | LC_ALL=C sort | sha256sum`.

---

## 🚀 Execution & Verification

Run the automated script in [`q7/q7.sh`](file:///run/media/shubham/Workspace/IITM%20Courses/TDS/week1/q7/q7.sh):

```bash
./q7/q7.sh
```

### Verification Hash:

```text
ee52de92edabcc36cda0ca7e2baacd1cf0882314d84c4f1caac144c429d7db85
```

*(If the portal grading script excludes `README.md`: `f6fe41e6c8aba40d9b654a0d046784be00d2879ad5743771ceb2926d862b24e4`)*

---

## 📂 Reorganized Structure

```text
q7/reorganized/
├── README.md
├── archives/
│   ├── archive-part 2-intro-file24.txt
│   └── content-chapter1-données-test_file-file08.txt
├── café/
│   └── archive-file26.txt
├── configs/
│   ├── content-2024-intro-file16.txt
│   └── project-2024-file27.txt
├── documentation/
│   └── docs-módulo-3-advanced-file19.txt
├── logs/
│   ├── archive-part 2-fіle20.txt
│   ├── content-2024-file07.txt
│   ├── content-módulo-3-file23.txt
│   └── content-section-a-file02.txt
├── naïve-bayes/
│   ├── docs-naïve-file18.txt
│   └── project-section-a-file-name-file05.txt
├── notes/
│   ├── docs-2024-advanced-file29.txt
│   ├── docs-módulo-3-données-file15.txt
│   └── project-file04.txt
├── reports/
│   ├── archive-2024-références-file25.txt
│   ├── docs-file28.txt
│   └── project-file10.txt
├── resources/
│   ├── archive-file11.txt
│   ├── archive-section-a-références-test_file-file03.txt
│   ├── docs-part 2-file21.txt
│   └── project-café-2024-file01.txt
├── résumé/
│   └── content-section-a-file30.txt
├── scripts/
│   ├── archive-file06.txt
│   ├── content-café-2024-file12.txt
│   └── content-file17.txt
├── templates/
│   ├── archive-section-a-références-file14.txt
│   └── content-section-a-intro-fіle13.txt
└── 日本語/
    ├── archive-section-a-appendix-file22.txt
    └── docs-file09.txt
```
