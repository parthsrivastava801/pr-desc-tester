---
name: pr-description-writer

description: |
  Writes concise, reviewer-friendly PR/MR descriptions—built strictly from the committed diff between
  the PR base and the latest push to the remote branch.

  By default this only drafts the description and writes it to `PR_DESCRIPTION.md`; it does not touch
  the hosting platform. Only when the user separately and explicitly asks to open, create, or update,
  close, or perform any other direct action on the actual PR/MR does it do so, after confirming the
  target.

  The skill supports two modes:
  1. **Description-generation mode** — analyze the diff and produce a structured description.
  2. **Direct-action mode** — the user supplies an inline description (or no description) and wants
     an immediate platform action (open, update description, close/abandon) without a diff analysis.

  Use this skill whenever the user asks to:
  - Write, generate, create, draft, or update a pull request (PR) or merge request (MR) description
  - Open, submit, push, or publish a new PR/MR
  - Update, edit, or change an existing PR/MR's title or description
  - Close, abandon, decline, or delete a PR/MR
  - Prepare a branch for review

  ## Trigger Phrases

This skill activates on any of the following kinds of requests (and natural variations of them):

### Description Generation
| Example Phrase | Action |
|---|---|
| "Write a PR description" | Generate description → write `PR_DESCRIPTION.md` |
| "Generate a PR description" | Same as above |
| "Draft a PR description" | Same as above |
| "Create a PR description" | Same as above |
| "Describe my changes" | Same as above |
| "Prepare my branch for review" | Same as above |
| "What should my PR say?" | Same as above |
| "Summarize my changes for a PR" | Same as above |

### Open / Create a PR (with optional inline description)
| Example Phrase | Action |
|---|---|
| "Open a PR" | Generate description → create PR |
| "Open a PR with the description 'Hello'" | **Direct-action**: skip diff analysis, use 'Hello' as body |
| "Create a new PR titled 'Fix auth bug'" | Direct-action: create PR with given title |
| "Submit a PR" | Generate description → create PR |
| "Push a PR" | Generate description → create PR |
| "Publish my PR" | Generate description → create PR |
| "Open a pull request targeting main" | Generate description → create PR against `main` |
| "Raise a PR" | Generate description → create PR |
| "Make a PR" | Generate description → create PR |

### Update an Existing PR
| Example Phrase | Action |
|---|---|
| "Update my PR description to 'Hello'" | **Direct-action**: update open PR body to 'Hello' |
| "Change my PR description" | Regenerate description → update open PR |
| "Edit my PR title to 'New title'" | Direct-action: update open PR title |
| "Update the PR" | Regenerate description → update open PR |
| "Refresh my PR description" | Regenerate description → update open PR |
| "Rewrite my PR description" | Regenerate description → update open PR |
| "Add reviewers to my PR" | Add specified reviewers to open PR |
| "Add labels to my PR" | Add specified labels to open PR |

### Close / Abandon a PR
| Example Phrase | Action |
|---|---|
| "Close my PR" | Close/decline/abandon the open PR on current branch |
| "Abandon my PR" | Same as above |
| "Decline my PR" | Same as above |
| "Cancel my PR" | Same as above |
| "Delete my PR" | Same as above (where supported by platform) |
| "Close PR #42" | Close the specified PR by number |



allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---


## Step 0 — Detect the Platform

Run this first. The result determines which reference file to load; load only that one file and read
nothing else from `references/`.

```bash
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if   echo "$REMOTE_URL" | grep -qiE "github\.com";       then PLATFORM="github"
elif echo "$REMOTE_URL" | grep -qiE "gitlab\.com|gitlab"; then PLATFORM="gitlab"
elif echo "$REMOTE_URL" | grep -qiE "bitbucket\.(org|com)"; then PLATFORM="bitbucket"
elif echo "$REMOTE_URL" | grep -qiE "visualstudio\.com|dev\.azure\.com|azure"; then PLATFORM="azure_devops"
elif echo "$REMOTE_URL" | grep -qiE "codecommit|amazonaws\.com"; then PLATFORM="aws_codecommit"
elif echo "$REMOTE_URL" | grep -qiE "gitea|forgejo"; then PLATFORM="gitea"
else PLATFORM="unsupported"
fi

echo "Platform: $PLATFORM"
```

- If `PLATFORM="unsupported"`: stop, tell the user _"This skill supports GitHub, GitLab, Bitbucket,
  Gitea, Azure DevOps, and AWS CodeCommit. The detected remote URL (`$REMOTE_URL`) does not match
  any of these — please confirm the remote or add support."_ Do not proceed further.
- Otherwise: load `references/${PLATFORM}.md` for all platform-specific commands (prerequisites,
  base-branch detection, scope commands, architectural-context commands, PR detection, and
  creating/updating PRs). Every command in the steps below is found there; do **not** read any other
  reference file.

---

## Core Philosophy

The description represents **exactly what a reviewer will see** — the committed diff on the platform,
not the working directory. The working directory is **never** a source of truth.

**Scope** = everything committed between `BASE` and `origin/HEAD` (the latest push).
**Context** = the committed repository state at `origin/HEAD`, read via Git-native commands.

Working-tree content (staged, unstaged, uncommitted) is excluded from both.

---

## Default Behavior & Routing

| Request type | Mode | Action |
|---|---|---|
| "Write/draft/generate a PR description" | Generation | Analyze diff → write `PR_DESCRIPTION.md`, report path, stop |
| "Create/open the PR" (no inline description) | Generation | Analyze diff → write description → create PR (confirm first) |
| "Open a PR with description 'X'" | **Direct-action** | Skip diff analysis → use 'X' as body → create PR |
| "Update my PR description to 'X'" | **Direct-action** | Skip diff analysis → patch open PR body to 'X' |
| "Edit my PR title to 'X'" | **Direct-action** | Skip diff analysis → patch open PR title to 'X' |
| "Close/abandon/decline my PR" | **Direct-action** | Skip diff analysis → close the open PR |
| "Add reviewers/labels" | **Direct-action** | Skip diff analysis → apply changes to open PR |

Never auto-publish without user intent. After writing `PR_DESCRIPTION.md` always ask "should I create the PR right now (yes/no)?" as a follow-up.

---

## Safety

Read-only only. Never run, execute, import, or evaluate any file from the repository (`python x.py`,
`node x.js`, notebook cells, test suites). Understand code by reading it. If running code seems absolutely
necessary, ask the user.

---

## Workflow

### Step 1 — Prerequisites & Fetch

See `references/${PLATFORM}.md → Prerequisites`. Verify tooling and run `git fetch origin --quiet`
before anything else. Stop and surface errors; never continue with stale refs.

### Step 2 — Identify the Base Branch

See `references/${PLATFORM}.md → Base Branch Detection`. Never hardcode branch names. If detection
falls through to the final fallback (`"main"`), flag this to the user and confirm before continuing.

### Step 3 — Determine PR Scope (latest push as reference)

The reference point is `origin/HEAD` — the last pushed commit on the remote tracking branch, **not**
local `HEAD`. This ensures the description reflects exactly what was pushed.

```bash
# Commits visible in the PR
git log origin/${BASE_BRANCH}..origin/HEAD --oneline

# Files changed
git diff origin/${BASE_BRANCH}...origin/HEAD --stat

# Full diff (scope)
git diff origin/${BASE_BRANCH}...origin/HEAD
```

Never use `git diff` (no ref), `git diff --cached`, or `git status` to gather description content.

> **If local HEAD is ahead of `origin/HEAD`**: unpushed commits exist. Inform the user — "X commit(s)
> are committed locally but not yet pushed and are excluded from this description. Push them first if
> you want them included." Do not include them automatically.

### Step 4 — Note Uncommitted Changes

```bash
git status --short
```

If dirty, inform the user and offer to wait for them to commit + push before regenerating. Never fold
working-tree changes into the description.

### Step 5 — Gather Architectural Context

Read the repository state at **`origin/HEAD`** (not local `HEAD`, not the filesystem):

```bash
git show origin/HEAD:path/to/file.py        # read a file
git ls-tree -r --name-only origin/HEAD      # list structure
git grep -n "<pattern>" origin/HEAD         # search
```

Use this to understand *why* changes were made — surrounding architecture, patterns, data flow. Do
not use the filesystem (`Read`/`Glob`/`Grep`) for anything that feeds the description.

### Step 6 — Review Commit Messages

```bash
git log origin/${BASE_BRANCH}..origin/HEAD --format="%h %s%n%b" | head -100
```

### Step 7 (Publish only) — Check for Existing Open PR/MR

Only when the user explicitly requests creating or updating the PR/MR. See
`references/${PLATFORM}.md → PR Detection`. Closed/merged PRs are never treated as active targets.

---

## Direct-Action Mode

Activated when the user provides an **explicit inline description or title**, or requests a **close/abandon/decline** action.

**When to enter Direct-Action Mode:**
- The user's message contains quoted or explicit description text (e.g. `"with the description 'Hello'"`)
- The user asks to close, abandon, decline, cancel, or delete the PR
- The user asks to add reviewers or labels only (no description change implied)

**Steps in Direct-Action Mode (replaces Steps 3–8):**

1. **Step 0** — Detect platform (always required).
2. **Step 1** — Run prerequisites + `git fetch origin --quiet` (always required).
3. **Step 2** — Detect base branch (required for create; skip for close/update).
4. **Skip Steps 3–8** — Do NOT run diff, stat, context, or commit-log commands.
5. **Step 7** — Check for an existing open PR (required for update/close; for create, verify none exists first if it does exit and warn the user).
6. **Execute the action** using the command from `references/${PLATFORM}.md`:

| Intent | Command section to use |
|---|---|
| Create new PR with inline description | `Creating & Updating PRs → Create` |
| Update open PR description/title | `Creating & Updating PRs → Update` |
| Close/abandon/decline PR | `Closing PRs` |
| Add reviewers/labels | `Creating & Updating PRs → reviewers/labels` |

**Inline description extraction rules:**
- Use text inside quotes as the exact PR body (preserve as-is, no reformatting).
- If the user provides a title separately (e.g. `"titled 'Fix auth'"`), use it; otherwise prompt for one or derive from branch name.
- If the user says close/abandon but gives no PR number, close the open PR on the current branch.

> **Note:** Direct-Action Mode never writes `PR_DESCRIPTION.md` unless the user also asks for a local copy.

---

## PR Description Structure

Real-world PRs are short and scannable. The template below is the standard; adapt length to the PR's
actual complexity — a one-file bugfix does not need diagrams.

```markdown
## What & Why
<!-- 2–4 sentences. What does this PR do and why now? -->

## Changes
| Area | What changed |
|------|-------------|
| **Module / Service** | Brief description |
| **API / Route** | Brief description |
| **Tests** | What's covered |

## How to Test
<!-- Automated: paste the exact command(s) -->
<!-- Manual: numbered steps only if commands aren't enough -->

## Notes
<!-- Breaking changes, deploy steps, env vars, migrations, open questions.
     Omit this section entirely if there's nothing worth flagging. -->
```

### Guidance by Section

**What & Why** — one paragraph max. Lead with the user/business reason, not the implementation.

**Changes table** — one row per logical area (not per file). Use the categories that apply:
Core logic · API/Routes · Models/Migrations · Tests · Config · Infra · Docs

**How to Test**
- Automated first, with the exact copy-pasteable command.
- Manual steps only when a human action is genuinely required.
- Skip if there is nothing to test.

**Notes** — use only when something would surprise the reviewer:
- Breaking API/contract change
- Required env vars or config before deploy
- Migration that needs a manual step
- Known limitation or follow-up ticket

**Diagrams** — include an ASCII or Mermaid diagram only when a flow is genuinely hard to follow from
the table alone (e.g. multi-step pipelines, state machines). Skip for simple CRUD changes.

### When to Add Diagrams

| Scenario | Format |
|---|---|
| Decision tree / branching logic | ASCII tree |
| Multi-step pipeline | Box diagram or Mermaid flowchart |
| State machine | Mermaid stateDiagram |
| Simple linear flow | Skip — use prose |

---

## Anti-Patterns to Avoid

1. **Wall of text** — use the table; avoid long paragraphs.
2. **Vague descriptions** — "misc fixes" tells reviewers nothing.
3. **Describing uncommitted or unpushed work** — scope is `origin/BASE...origin/HEAD`, always.
4. **Listing every file** — the Changes table groups by area, not file.
5. **Hardcoded base branch** — always detect; never assume `main`/`master`.
6. **Diagram for everything** — only when the flow is non-obvious.
7. **Describing only the latest commit** — cover all commits in the push range.

---

## Output

**First: determine which mode applies.**

### Generation Mode (default)
1. Detect platform (Step 0). Load only `references/${PLATFORM}.md`.
2. Run prerequisites + fetch (Step 1).
3. Detect base branch (Step 2).
4. Compute scope from `origin/BASE...origin/HEAD` (Step 3).
5. Note unpushed local commits if any (Step 3 note).
6. Gather context from `origin/HEAD` via Git-native commands (Step 5).
7. Review commit messages (Step 6).
8. Write the description using the template above.
9. Self-check: cross-reference the file list and feature claims against `--stat` and commit log.
10. Write to `PR_DESCRIPTION.md` (or user-specified path):

```bash
cat > PR_DESCRIPTION.md << 'EOF'
<full PR description markdown>
EOF
```

Report the file path. Ask the user if they want to create a PR using that description (yes/no).

11. **Only when explicitly asked** to create or update: check for open PR (Step 7), then use the
    create or update command from `references/${PLATFORM}.md`. Always pass the detected `$BASE_BRANCH`.
12. Be ready to iterate based on user feedback.

### Direct-Action Mode
1. Detect platform (Step 0). Load only `references/${PLATFORM}.md`.
2. Run prerequisites + fetch (Step 1).
3. Detect base branch (Step 2) — skip for close/update-only actions.
4. Check for open PR (Step 7) — required for update/close.
5. Execute the action directly (create with inline body, update title/body, or close).
6. Report the result (PR URL, PR number, or confirmation of closure). Do **not** write `PR_DESCRIPTION.md`.
