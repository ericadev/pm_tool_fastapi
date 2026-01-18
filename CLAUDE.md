## ⚠️ CRITICAL: Feature Branch Workflow

**🔴 NEVER COMMIT DIRECTLY TO `main` BRANCH 🔴**

All development work must be done on feature branches. This ensures:
- The `main` branch remains stable and production-ready
- Changes can be reviewed before integration
- Easy rollback if issues arise
- Clear development history
- Isolated development without conflicts

---

## Git Workflow

### 1. Creating a Feature Branch

Before starting any work, create a new feature branch from `main`:

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name
```

### 2. Working on Your Branch

Make your changes and commit regularly:

```bash
# Stage your changes
git add .

# Or stage specific files
git add src/components/NewComponent.tsx

# Commit with a descriptive message
git commit -m "Add habit creation form component"
```

### 3. Pushing Your Branch

Push your feature branch to the remote repository:

```bash
# First time pushing a new branch
git push -u origin feature/your-feature-name

# Subsequent pushes
git push
```

### 4. Merging to Main

Once your feature is complete and tested:

```bash
# Switch to main
git checkout main

# Pull latest changes
git pull origin main

# Merge your feature branch
git merge feature/your-feature-name

# Push to remote
git push origin main

# Optional: Delete the feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Branch Naming Conventions

Use clear, descriptive branch names with prefixes:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New features or enhancements | `feature/streak-badge` |
| `fix/` | Bug fixes | `fix/date-calculation-bug` |
| `docs/` | Documentation updates | `docs/update-readme` |
| `refactor/` | Code refactoring (no functional changes) | `refactor/state-management` |
| `test/` | Adding or updating tests | `test/habit-service-tests` |
| `chore/` | Maintenance, dependencies, tooling | `chore/update-dependencies` |

### Examples

```bash
git checkout -b feature/habit-calendar-view
git checkout -b fix/streak-calculation-error
git checkout -b docs/add-api-documentation
git checkout -b refactor/extract-date-utils
git checkout -b test/add-habit-form-tests
git checkout -b chore/configure-eslint
```

---

## Commit Message Guidelines

Write clear, descriptive commit messages that explain **what** changed and **why**:

### Format

```
<type>: <brief description>

<optional detailed explanation>
```

### Good Examples

```bash
git commit -m "feat: Add habit creation modal with form validation"
git commit -m "fix: Correct streak calculation for edge cases"
git commit -m "refactor: Extract date utilities to separate module"
git commit -m "docs: Add component usage examples to README"
git commit -m "test: Add unit tests for streak calculator"
git commit -m "chore: Update Tailwind CSS to v3.4.0"
```

### Bad Examples

❌ `git commit -m "fixed stuff"`
❌ `git commit -m "update"`
❌ `git commit -m "WIP"`
❌ `git commit -m "asdf"`

---

## Development Best Practices

### 1. Keep Branches Focused

- One feature/fix per branch
- Avoid mixing unrelated changes
- Keep branches short-lived (merge within a few days)

### 2. Commit Frequently

- Commit logical units of work
- Don't wait until everything is perfect
- Small commits are easier to review and debug

### 3. Test Before Pushing

```bash
# Run the development server
npm run dev

# Build the project (check for errors)
npm run build

# Run tests (when available)
npm test
```

### 4. Keep Your Branch Updated

Regularly sync with `main` to avoid conflicts:

```bash
git checkout main
git pull origin main
git checkout feature/your-branch
git merge main
```

---

## Example Workflow

Here's a complete workflow for adding a new feature:

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/add-stats-dashboard

# 3. Make changes
# ... edit files ...

# 4. Stage and commit
git add src/pages/Stats.tsx
git commit -m "feat: Create stats dashboard page layout"

# 5. Continue working
# ... more edits ...

git add src/components/stats/
git commit -m "feat: Add completion chart and heatmap components"

# 6. Push feature branch
git push -u origin feature/add-stats-dashboard

# 7. When feature is complete, merge to main
git checkout main
git pull origin main
git merge feature/add-stats-dashboard
git push origin main

# 8. Clean up
git branch -d feature/add-stats-dashboard
git push origin --delete feature/add-stats-dashboard
```

---

## Quick Reference

### Common Commands

```bash
# Check current branch
git branch

# See all branches
git branch -a

# Switch branches
git checkout <branch-name>

# Create and switch to new branch
git checkout -b <branch-name>

# See changes
git status
git diff

# Delete local branch
git branch -d <branch-name>

# Delete remote branch
git push origin --delete <branch-name>
```

### Emergency: Need to Switch Branches with Uncommitted Changes?

```bash
# Stash your changes
git stash

# Switch branches
git checkout other-branch

# Come back and restore changes
git checkout your-branch
git stash pop
```

---

## Questions?

If you're unsure about the workflow:
1. Check this document
2. Review [TODO.md](TODO.md) for project structure
3. Look at recent commit history: `git log --oneline`

---

**Remember: Always use feature branches. Never commit directly to `main`.**
