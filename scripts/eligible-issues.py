#!/usr/bin/env python3
"""Print the open issues of a repo that the agent-crew may work on, one number per line.

  eligible-issues.py <owner/repo>        (uses `gh`; GH_TOKEN selects the account)

An issue is eligible when
  - its author is the repo owner, an org member or a collaborator, or
  - someone with write access (write, maintain or admin) added the `crew-approved` label,
    and the issue text has not been edited since that label was added.
Issue text is untrusted input to an agent that holds a write token, so trust is decided
here, in code, before the agent reads anything.
"""
import json
import subprocess
import sys

TRUSTED_AUTHORS = {"OWNER", "MEMBER", "COLLABORATOR"}
APPROVE_LABEL = "crew-approved"
QUERY = """
query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    issues(states: OPEN, first: 50, after: $after) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number authorAssociation lastEditedAt
        timelineItems(itemTypes: [LABELED_EVENT], last: 50) {
          nodes { ... on LabeledEvent { createdAt label { name } actor { login } } }
        }
      }
    }
  }
}"""


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"eligible-issues: gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout


_perm = {}


def can_write(repo, login):
    if login not in _perm:
        r = subprocess.run(["gh", "api", f"repos/{repo}/collaborators/{login}/permission", "-q", ".permission"],
                           capture_output=True, text=True)
        _perm[login] = r.stdout.strip() in ("admin", "maintain", "write")
    return _perm[login]


def eligible(issue, can_write_fn):
    if issue["authorAssociation"] in TRUSTED_AUTHORS:
        return True
    approvals = [e["createdAt"] for e in issue["timelineItems"]["nodes"]
                 if e and e["label"]["name"] == APPROVE_LABEL and e.get("actor")
                 and can_write_fn(e["actor"]["login"])]
    # ISO 8601 timestamps in UTC compare correctly as strings.
    return bool(approvals) and (issue["lastEditedAt"] is None or issue["lastEditedAt"] <= max(approvals))


def main():
    if len(sys.argv) != 2 or "/" not in sys.argv[1]:
        sys.exit(__doc__)
    repo = sys.argv[1]
    owner, name = repo.split("/", 1)
    after = None
    while True:
        args = ["api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={owner}", "-F", f"name={name}"]
        if after:
            args += ["-F", f"after={after}"]
        issues = json.loads(gh(*args))["data"]["repository"]["issues"]
        for i in issues["nodes"]:
            if eligible(i, lambda login: can_write(repo, login)):
                print(i["number"])
        if not issues["pageInfo"]["hasNextPage"]:
            break
        after = issues["pageInfo"]["endCursor"]


if __name__ == "__main__":
    main()
