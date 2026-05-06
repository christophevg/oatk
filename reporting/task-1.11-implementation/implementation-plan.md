# Implementation Plan: Complete Task 1.11 - Remove MANIFEST.in

## Status

- **Updated**: `.gitignore` (added Python cache exclusions)
- **Pending**: Delete `MANIFEST.in` file
- **Pending**: Verify build works
- **Pending**: Verify tests pass
- **Pending**: Update TODO.md

## What Has Been Done

### 1. Updated .gitignore

**File**: `/Users/xtof/Workspace/agentic/oatk/.gitignore`

**Changes**:
- Added `__pycache__/` to ignore Python cache directories
- Added `*.py[cod]` to ignore compiled Python files

**Result**: Git will now properly ignore Python cache files, ensuring hatchling includes all package files.

## What Needs to Be Done

### 2. Delete MANIFEST.in File

**Action**: Remove the MANIFEST.in file from the repository

**Command**:
```bash
git rm MANIFEST.in
```

**Why**: MANIFEST.in is setuptools-specific and not used by hatchling. All package data files are already inside the package directory, so hatchling will include them automatically.

### 3. Verify Build Works

**Action**: Build the package and verify no errors

**Command**:
```bash
make dist
```

**Expected**: Build completes successfully, creating:
- `dist/oatk-<version>-py3-none-any.whl`
- `dist/oatk-<version>.tar.gz`

### 4. Verify Package Data is Included

**Action**: Check that package data files are in the wheel

**Command**:
```bash
unzip -l dist/oatk-*.whl | grep -E "(static|templates|js)" | grep -v __pycache__
```

**Expected Output**: Should show:
- `oatk/fake/static/oatk.js`
- `oatk/fake/static/style.css`
- `oatk/fake/templates/base.html`
- `oatk/fake/templates/home.html`
- `oatk/fake/templates/create_client.html`
- `oatk/fake/templates/login.html`
- `oatk/fake/templates/dialog.html`
- `oatk/fake/templates/authorize.html`
- `oatk/js/oatk.js`

### 5. Run Tests

**Action**: Ensure all tests pass after the change

**Command**:
```bash
make test
```

**Expected**: All tests pass (no new failures)

### 6. Run Lint

**Action**: Ensure code quality checks pass

**Command**:
```bash
make lint
```

**Expected**: No linting errors

### 7. Update TODO.md

**Action**: Mark task 1.11 implementation as complete

**Change**: The task is already marked as done with investigation. No additional TODO.md update needed beyond noting the implementation is complete.

### 8. Commit Changes

**Action**: Commit the changes with conventional commit format

**Command**:
```bash
git add .gitignore
git commit -m "chore: remove MANIFEST.in (not needed for hatchling)

- Updated .gitignore with comprehensive Python cache exclusions
- Removed MANIFEST.in (setuptools-specific, not used by hatchling)
- All package data files are in package directory, auto-included by hatchling
- No pyproject.toml configuration needed

Investigation: analysis/manifest-investigation.md"
```

## Automated Execution Script

A Python script has been created at `/Users/xtof/Workspace/agentic/oatk/remove_manifest.py` that automates steps 2-4:

```bash
python remove_manifest.py
```

This script will:
1. Remove MANIFEST.in
2. Run `uv build`
3. Verify package data is included

## Verification Checklist

After executing all steps:

- [ ] MANIFEST.in file deleted
- [ ] Build succeeds (`make dist`)
- [ ] Package data files in wheel (static/, templates/, js/)
- [ ] Tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Changes committed to git

## Technical Context

### Why MANIFEST.in is Not Needed

From `/Users/xtof/Workspace/agentic/oatk/analysis/manifest-investigation.md`:

1. **Setuptools-specific**: MANIFEST.in is only used by setuptools, not hatchling
2. **Package data location**: All data files are inside `oatk/` package directory:
   - `oatk/fake/static/*` - Static files (oatk.js, style.css)
   - `oatk/fake/templates/*` - Template files (HTML templates)
   - `oatk/js/*` - JavaScript files (oatk.js)
3. **Hatchling behavior**: Automatically includes all files in package directory that aren't ignored by `.gitignore`
4. **No configuration needed**: Default hatchling behavior is sufficient

### .gitignore Additions

The updated `.gitignore` now includes:
- `__pycache__/` - Python cache directories
- `*.py[cod]` - Compiled Python files (.pyc, .pyo, .pyd)

These additions ensure Python cache files are properly excluded from builds.

## Files Modified

- **Modified**: `.gitignore` - Added `__pycache__/` and `*.py[cod]`
- **Deleted**: `MANIFEST.in` - No longer needed for hatchling builds
- **Created**: `remove_manifest.py` - Verification script (temporary)

## References

- Investigation: `/Users/xtof/Workspace/agentic/oatk/analysis/manifest-investigation.md`
- Development Summary: `/Users/xtof/Workspace/agentic/oatk/reporting/task-1.11-implementation/development-summary.md`
- Build Backend: Hatchling (configured in `pyproject.toml`)