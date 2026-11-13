# Writing an agent-crew issue

Every issue on Idle-Sync/agent-crew follows this blueprint, whoever writes it: a person on the
GitHub form, or a crew agent filing a follow-up.

## Before you write

1. **Search first.** `gh issue list --repo Idle-Sync/agent-crew --search "<three key words>" --state all`.
   If one already covers it, add your case as a comment there.
2. **One problem per issue.** Several symptoms of one cause are one issue: list them all.
3. **Nothing private.** No tokens, private repo names you do not want public, or code from private repos.

## Kinds

| Kind | Use it when |
|---|---|
| `bug` | the crew did something its docs or briefs say it should not, or the `crew` CLI failed |
| `workflow` | a rule in a brief is missing or wrong: the agent did what it was told, and that is the problem |
| `idea` | something new the crew does not do at all |
| `pushback` | an agent and the owner disagreed, and one of them was right; say which and why |

## Title

`<kind>: <what is wrong, in about six words>`. Name the problem, not the fix.

## Body

Use these four headings, in this order.

```
## What happened / what is wanted
<what you saw or want. For a bug, the command you ran or the PR/issue the agent touched, and what it did.>

## Expected
<what should have happened. If you know where it goes wrong (which brief rule, which crew command), say so.>

## Evidence
- agent-crew <version>, mode <local or ci>, OS <Linux, macOS>
- `crew status` output, the relevant lines of the agent's state.md, or links to the PR/issue/review involved

## Repro or example
<the shortest steps that show it, or a concrete example of the idea in use>
```

## Labels

Leave labels to the maintainers.
