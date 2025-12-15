# Git & GitHub Quick Reference

This file lists common Git and GitHub commands useful when working with this repository.

**Clone repository:**
- `git clone <repo-url>`

**Check status / log:**
- `git status`
- `git log --oneline --graph --decorate --all`

**Branching:**
- `git branch` : list branches
- `git branch <name>` : create branch
- `git checkout <name>` : switch branch
- `git switch -c <name>` : create and switch (newer syntax)

**Staging & committing:**
- `git add <file>` or `git add .`
- `git commit -m "Short descriptive message"`
- `git commit --amend` : amend last commit

**Pushing & pulling:**
- `git push origin <branch>`
- `git push -u origin <branch>` : set upstream
- `git pull` : fetch + merge
- `git fetch` : download remote refs

**Working with remotes:**
- `git remote -v` : show remotes
- `git remote add origin <repo-url>`

**Merging & rebasing:**
- `git.merge <branch>` : merge into current branch
- `git rebase <branch>` : reapply commits on top of branch

**Stash:**
- `git stash` : save local changes
- `git stash pop` : apply and remove stash

**Undo / reset:**
- `git checkout -- <file>` : discard unstaged changes
- `git reset --soft HEAD~1` : undo last commit, keep changes staged
- `git reset --hard HEAD~1` : undo last commit and discard changes (dangerous)

**Inspect & diff:**
- `git diff` : show unstaged changes
- `git show <commit>` : show a commit
- `git blame <file>` : see who changed lines

**Tags & releases:**
- `git tag -a v1.0 -m "v1.0"` : create annotated tag
- `git push origin v1.0` : push tag

**Pull request workflow (basic):**
- Create a branch: `git switch -c feature/xyz`
- Work and commit locally
- Push branch: `git push -u origin feature/xyz`
- Open a Pull Request on GitHub from `feature/xyz` into `main` (or `master`)

**Resolving merge conflicts (high level):**
- After `git pull` or `git merge`, open conflicted files and resolve markers
- `git add <resolved-file>` then `git commit`

Notes:
- Use meaningful commit messages and small focused commits.
- Prefer feature branches and open PRs for collaborative review.
- When unsure, make a local backup branch before destructive commands.

For repository-specific workflows (branch naming, CI, PR templates), check project documentation or ask the maintainers.
