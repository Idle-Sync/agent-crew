This adds the agent-crew to this repository as two GitHub Actions workflows:

- **agent-crew fixer** (`.github/workflows/agent-crew-fixer.yml`): on new or labelled issues, on a "changes requested" review, and hourly, it fixes the highest-priority open issue and opens one PR for it.
- **agent-crew reviewer** (`.github/workflows/agent-crew-reviewer.yml`): reviews every PR when it opens or gets new commits, merges the ones that pass, files follow-ups, and once a day decides whether to cut a release.

Their instructions are in `.github/agent-crew/fixer.md` and `.github/agent-crew/reviewer.md`. Edit them to change how the crew works in this repo.

## Before merging: add these repository secrets

Settings → Secrets and variables → Actions:

| Secret | What |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` | Claude access. The OAuth token comes from `claude setup-token` (uses your Claude plan); an API key is billed per use. Add one of the two. |
| `CREW_FIXER_TOKEN` | A GitHub token for the account the fixer works as (contents and pull requests: write; issues: write). |
| `CREW_REVIEWER_TOKEN` | A GitHub token for the account the reviewer works as. Use a second account if you want formal approvals: GitHub does not let an account approve its own PR. |

Tokens from a real account (not the default `GITHUB_TOKEN`) are needed so the fixer's PRs trigger the reviewer's workflow.

## Turning it off

Disable either workflow in the Actions tab, or delete the two workflow files.
