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
        labels(first: 100) { nodes { name } }
        timelineItems(itemTypes: [LABELED_EVENT, RENAMED_TITLE_EVENT], last: 100) {
          nodes {
            __typename
            ... on LabeledEvent { createdAt label { name } actor { login } }
            ... on RenamedTitleEvent { createdAt actor { login } }
          }
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
    # The label must be on the issue now (a removed approval no longer counts) ...
    if APPROVE_LABEL not in {l["name"] for l in issue["labels"]["nodes"]}:
        return False
    events = [e for e in issue["timelineItems"]["nodes"] if e]
    adds = [e for e in events if e["__typename"] == "LabeledEvent" and e["label"]["name"] == APPROVE_LABEL]
    if not adds:
        return False
    # ... and whoever added it most recently must have write access; that is the approval.
    last_add = max(adds, key=lambda e: e["createdAt"])
    if not (last_add.get("actor") and can_write_fn(last_add["actor"]["login"])):
        return False
    approved = last_add["createdAt"]  # ISO 8601 UTC: string order is time order
    # Any change to the text after approval, other than a title change by a writer, voids it.
    if issue["lastEditedAt"] is not None and issue["lastEditedAt"] > approved:
        return False
    for e in events:
        if e["__typename"] == "RenamedTitleEvent" and e["createdAt"] > approved:
            if not (e.get("actor") and can_write_fn(e["actor"]["login"])):
                return False
    return True


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
