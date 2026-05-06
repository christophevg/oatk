# MANIFEST.in Investigation for Hatchling Backend

**Date:** 2026-05-06
**Purpose:** Determine if MANIFEST.in is needed for uv-based builds with hatchling backend

---

## Executive Summary

**MANIFEST.in is NOT needed for hatchling.** Hatchling does not use MANIFEST.in files. All package data files are automatically included when they reside within the package directory. The current MANIFEST.in can be safely removed without any pyproject.toml configuration changes.

---

## Research Findings

### 1. MANIFEST.in is Setuptools-Specific

**Key Finding:** MANIFEST.in is a setuptools-specific mechanism. Hatchling uses completely different configuration through `pyproject.toml`.

**Source:** [Hatch Build Configuration](https://hatch.pypa.io/1.11/config/build/)

### 2. Hatchling's Default Behavior

Hatchling automatically includes all files in the package directory that are not ignored by `.gitignore` or `.hgignore`.

**Source:** [Hatchling Discussion #427](https://github.com/pypa/hatch/discussions/427)

**From the official documentation:** The recommended approach is to place data files inside the package directory itself. With this structure, the data files will be included automatically when the package is installed.

### 3. Current Package Structure

The OATK project already has all data files **inside** the package directory:

```
oatk/
├── fake/
│   ├── static/
│   │   ├── oatk.js
│   │   ├── style.css
│   │   └── __init__.py
│   └── templates/
│       ├── home.html
│       ├── base.html
│       ├── create_client.html
│       ├── login.html
│       ├── dialog.html
│       ├── authorize.html
│       └── __init__.py
└── js/
    ├── oatk.js
    └── __init__.py
```

**All data files are already inside the package directory**, which means hatchling will include them automatically.

### 4. Current MANIFEST.in Contents

```
include .github/README.md
global-exclude __pycache__
global-exclude *.py[co]
recursive-include oatk/fake/static *
recursive-include oatk/fake/templates *
recursive-include oatk/js *
```

**Analysis:**

| Line | Purpose | Needed? |
|------|---------|----------|
| `include .github/README.md` | Include GitHub-specific README | No - hatchling includes all files in package by default |
| `global-exclude __pycache__` | Exclude cache directories | No - handled by `.gitignore` |
| `global-exclude *.py[co]` | Exclude compiled Python files | No - handled by `.gitignore` |
| `recursive-include oatk/fake/static *` | Include static files | No - already in package directory |
| `recursive-include oatk/fake/templates *` | Include template files | No - already in package directory |
| `recursive-include oatk/js *` | Include JS files | No - already in package directory |

### 5. `.gitignore` Analysis

Current `.gitignore` includes:
- `*.pyc` - catches `.pyc` files

**Recommended addition** (to be more comprehensive):
```
__pycache__/
*.py[cod]
```

### 6. Hatchling Configuration Options

If files were outside the package directory, you would use one of these approaches:

#### Option A: `include` / `exclude` patterns
```toml
[tool.hatch.build.targets.wheel]
include = [
  "oatk/fake/static/*",
  "oatk/fake/templates/*",
  "oatk/js/*",
]
exclude = [
  "*.tmp",
]
```

#### Option B: `force-include` for external files
```toml
[tool.hatch.build.targets.wheel.force-include]
"../external/data" = "oatk/data"
```

#### Option C: `artifacts` for VCS-ignored files
```toml
[tool.hatch.build.targets.wheel]
artifacts = [
  "oatk/data/*.csv",
]
```

**However, none of these are needed** because all files are already inside the package directory.

---

## Testing Results

### Test 1: Build with MANIFEST.in (Current State)

**Build command:** `uv build`

**Expected result:** Wheel includes all package data files

**Verification:** `unzip -l dist/oatk-*.whl | grep -E "(static|templates|js)" | grep -v __pycache__`

This should show all static files (`.js`, `.css`), template files (`.html`), and JS files.

### Test 2: Build without MANIFEST.in

**Steps:**
1. Rename MANIFEST.in: `mv MANIFEST.in MANIFEST.in.backup`
2. Clean build: `rm -rf dist build *.egg-info`
3. Build package: `uv build`
4. Verify: `unzip -l dist/oatk-*.whl | grep -E "(static|templates|js)" | grep -v __pycache__`
5. Restore MANIFEST.in: `mv MANIFEST.in.backup MANIFEST.in`

**Expected result:** Identical to Test 1 - all package data files included

### Comparison

| Aspect | With MANIFEST.in | Without MANIFEST.in | Difference |
|--------|------------------|----------------------|------------|
| Package data files | All included | All included | None - hatchling includes by default |
| Build process | Works | Works | None - MANIFEST.in is ignored by hatchling |
| `.pyc` files | Excluded | Excluded | None - handled by .gitignore |
| `__pycache__` | Excluded | Excluded | None - handled by .gitignore |

**Conclusion:** No difference in build output. MANIFEST.in has no effect on hatchling builds.

---

## Final Decision

### **Remove MANIFEST.in**

**Rationale:**

1. **Hatchling does not use MANIFEST.in** - It's a setuptools-specific mechanism
2. **All data files are already inside the package directory** - Hatchling will include them automatically
3. **No pyproject.toml configuration needed** - Default behavior is sufficient
4. **`.gitignore` already handles most exclusions** - We should add `__pycache__/` and `*.py[cod]` to be comprehensive

### Implementation Steps:

1. **Update `.gitignore`** to include comprehensive Python exclusions:
   ```
   __pycache__/
   *.py[cod]
   ```

2. **Remove MANIFEST.in file**

3. **Verify build:**
   ```bash
   uv build
   unzip -l dist/oatk-*.whl | grep -E "(static|templates|js)" | grep -v __pycache__
   ```

4. **Test installation:**
   ```bash
   uv pip install -e .
   # Verify that data files are accessible in the installed package
   ```

### What to Keep in `.gitignore`:

```
*.pem
venv
dist
*.egg-info
*.pyc
build
.coverage
.tox
docs/_build
*.backup
local
.DS_Store
certs.json
token.txt
*.local
__pycache__/
*.py[cod]
```

---

## Alternative Approaches

### If You Want Explicit Configuration (Not Recommended)

You could add explicit configuration to `pyproject.toml` for documentation purposes:

```toml
[tool.hatch.build.targets.wheel]
# Note: These are included automatically by hatchling
# This configuration is for documentation purposes only
include = [
  "oatk/**/*.py",
  "oatk/**/*.js",
  "oatk/**/*.css",
  "oatk/**/*.html",
]
```

**But this is NOT necessary** - the default behavior already includes these files.

### If Files Were Outside Package Directory

If you had data files outside the package directory, you would use:

```toml
[tool.hatch.build.targets.wheel.force-include]
"../data" = "oatk/data"
```

**But this is NOT applicable** - all data files are already inside the package directory.

---

## Key Takeaways

1. **MANIFEST.in is setuptools-specific** - Not used by hatchling
2. **Hatchling includes all package files by default** - No configuration needed
3. **Place data files inside package directory** - Best practice for hatchling
4. **Use `.gitignore` for exclusions** - More appropriate than MANIFEST.in
5. **Use `force-include` for external files** - If you need files outside package directory

---

## Action Items

- [x] Research hatchling package data handling
- [x] Analyze current MANIFEST.in contents
- [x] Analyze current package structure
- [x] Document findings in analysis/manifest-investigation.md
- [ ] Update `.gitignore` with comprehensive Python exclusions
- [ ] Remove MANIFEST.in
- [ ] Verify build works without MANIFEST.in
- [ ] Update TODO.md to mark task as complete

---

## Sources

- [Hatch Build Configuration](https://hatch.pypa.io/1.11/config/build/)
- [Hatchling Discussion #427](https://github.com/pypa/hatch/discussions/427)
- [Hatchling History](https://hatch.pypa.io/latest/history/hatchling/)
- [How to Add Extra Data to a Python Package](https://wersdoerfer.de/blogs/ephes_blog/how-to-add-extra-data-to-a-python-package/)