# Fork workflow

This is a fork of [plamish/xcomfort](https://github.com/plamish/xcomfort) maintained at
[SEspe/xcomfort](https://github.com/SEspe/xcomfort). It exists to run patched locally **and**
to feed fixes back upstream, so the branch layout keeps those two goals from colliding.

This file lives on `personal` only — it must never appear in a PR to upstream.

## Branches

| Branch | Purpose | Rules |
| --- | --- | --- |
| `master` | Pure mirror of `upstream/master` | Never commit here. Only ever fast-forwarded from upstream. |
| `personal` | What actually runs in Home Assistant | Default branch on GitHub. Merges topic branches + fork-only commits. |
| `fix/*`, `feat/*` | One logical change each | Branched off `master`. Kept PR-clean: no fork-only cruft. |

Upstream is receptive but slow — every external PR it has received was merged, but there have
been no commits since June 2025. So never wait on an upstream merge before using a fix; land it
on `personal` and let the PR catch up.

## Remotes

```
origin    https://github.com/SEspe/xcomfort.git    (fetch + push)
upstream  https://github.com/plamish/xcomfort.git  (fetch only)
```

`upstream`'s push URL is deliberately set to `DISABLED_use_a_PR_instead` so a stray
`git push upstream` fails loudly instead of doing something surprising.

## Day-to-day

**Start a change** — always off an up-to-date `master`, never off `personal`:

```sh
git fetch upstream
git checkout master && git merge --ff-only upstream/master
git checkout -b fix/short-description master
```

**Use it locally** — merge the topic branch into `personal` and deploy:

```sh
git checkout personal && git merge fix/short-description
git push origin personal
```

**Offer it upstream** — push the topic branch on its own and open the PR from there:

```sh
git push origin fix/short-description
gh pr create --repo plamish/xcomfort --base master --head SEspe:fix/short-description
```

**Sync after upstream moves:**

```sh
git fetch upstream
git checkout master && git merge --ff-only upstream/master
git checkout personal && git merge master
```

If upstream merged one of your topic branches, that merge is a no-op or a trivial conflict —
the same change arriving from two directions. Resolve in favour of upstream's version and
delete the topic branch.

## Fork-only changes

These stay on `personal` and are **never** included in a topic branch, because they would make a
PR unreviewable:

- `FORK.md` (this file)
- Any `manifest.json` version bump used to force a HACS update
- Any retargeting of `documentation` / `issue_tracker` / `codeowners` away from `plamish`

Keep them in as few commits as possible so they are easy to spot and rebase.

## Installing this fork in Home Assistant

The fork publishes no GitHub releases, so HACS falls back to the repository's **default branch** —
which is why `personal` is the default rather than `master`.

HACS → three-dot menu → Custom repositories → `https://github.com/SEspe/xcomfort`,
category **Integration**. Then install, and restart Home Assistant.

To make HACS offer an update after new work lands on `personal`, bump `version` in
`custom_components/xcomfort/manifest.json` (a fork-only commit — see above). Note it currently
reads `1.3.5` while upstream's last commits bumped to 1.3.7; upstream simply forgot to update it.

## Known upstream issues worth fixing

- [#44](https://github.com/plamish/xcomfort/issues/44) — blocking I/O in the event loop
- [#48](https://github.com/plamish/xcomfort/issues/48) — battery inputs missing after integration
- [#46](https://github.com/plamish/xcomfort/issues/46) — won't load on 2025.6.0 (check whether
  PR #47's deprecation fixes already covered this before spending time on it)
