# xcomfort — fork notes

This repository continues [plamish/xcomfort](https://github.com/plamish/xcomfort), the Eaton
xComfort SHC integration for Home Assistant. Upstream has been dormant since **2025-06-15** with
16 open issues and no maintainer replies, and none of its other 10 forks are being maintained
either. This fork is therefore treated as the maintained line rather than as a patch queue.

Upstream is *not* archived, so the door back is deliberately kept open — see [Branches](#branches).

## Branches

| Branch | Purpose | Rules |
| --- | --- | --- |
| `main` | The maintained line. What runs in Home Assistant. | Default branch on GitHub. Small fixes land here directly. |
| `master` | Untouched mirror of `upstream/master` | Never commit here. Only ever fast-forwarded from upstream. |
| `fix/*`, `feat/*` | A change worth offering upstream | Branched off `master`, kept free of fork-specific commits. |

Keeping `master` and the `upstream` remote costs nothing and is the insurance policy: if plamish
returns, or if the integration finds a new home, work can still be offered as a clean PR.

## Remotes

```
origin    https://github.com/SEspe/xcomfort.git    (fetch + push)
upstream  https://github.com/plamish/xcomfort.git  (fetch only)
```

`upstream`'s push URL is deliberately set to `DISABLED_use_a_PR_instead`, so a stray
`git push upstream` fails loudly instead of doing something surprising.

## Day-to-day

Most work is just a commit on `main`:

```sh
git checkout main
# ...edit, commit...
git push origin main
```

**When a change is self-contained enough to offer upstream** — build it off `master` so the PR
carries none of this fork's own commits, then merge it into `main` to actually use it:

```sh
git fetch upstream
git checkout master && git merge --ff-only upstream/master
git checkout -b fix/short-description master
# ...edit, commit...
git push origin fix/short-description
gh pr create --repo plamish/xcomfort --base master --head SEspe:fix/short-description
git checkout main && git merge fix/short-description
```

**If upstream ever moves again:**

```sh
git fetch upstream
git checkout master && git merge --ff-only upstream/master
git checkout main && git merge master
```

## Releases

HACS installs from the latest GitHub release, and falls back to the default branch when a
repository has none. Cutting a tag per meaningful change gives HACS a proper update prompt:

```sh
# bump "version" in custom_components/xcomfort/manifest.json first
git tag v1.3.8 && git push origin v1.3.8
gh release create v1.3.8 --title v1.3.8 --notes "..."
```

Versioning continues upstream's sequence — upstream's last code was 1.3.7, so this fork starts at
**1.3.8**. Note that upstream's `manifest.json` was left at 1.3.5 by mistake while the code went to
1.3.7, and the `###Version` header comments at the top of each module were never kept in sync with
each other. Those headers are left alone on purpose: rewriting them all would create pointless
conflicts against any future upstream merge. `manifest.json` and `const.py` are the versions that
matter.

## Divergence from upstream

Changes made here that are intentionally *not* upstream material:

- `FORK.md` (this file)
- `manifest.json`: `documentation`, `issue_tracker` and `codeowners` retargeted from `@plamish`
  to `@SEspe`, so Home Assistant points users at the repo that is actually maintained

## Installing in Home Assistant

HACS → three-dot menu → **Custom repositories** → `https://github.com/SEspe/xcomfort`,
category **Integration** → install → restart Home Assistant.

### Migrating an existing upstream install

Home Assistant keys config entries, devices and entities off the integration **domain**
(`xcomfort`) and the config entry's ID — never off which repository the files came from. This fork
keeps the same domain and the same `custom_components/xcomfort/` path, so entity IDs, recorder
history, automations, dashboards and area assignments all carry over untouched.

1. Take a Home Assistant backup (Settings → System → Backups).
2. HACS → xComfort SHC (the `plamish` one) → three-dot menu → **Remove**. This deletes the files
   but the running integration stays loaded in memory, so nothing stops working yet.
3. HACS → Custom repositories → add `https://github.com/SEspe/xcomfort` as an **Integration**.
4. Install it, then restart Home Assistant **once**.

> **Never** remove the integration under Settings → Devices & Services. *That* deletes the config
> entry, and with it the entity IDs and their history. Only ever touch HACS.

Do steps 2–4 in one sitting. If Home Assistant does restart while the files are missing, the
config entry is not lost — it just fails to set up, and recovers once the files are back.

## Known upstream issues worth fixing

- [#44](https://github.com/plamish/xcomfort/issues/44) — blocking I/O in the event loop
- [#48](https://github.com/plamish/xcomfort/issues/48) — battery inputs missing after integration
- [#46](https://github.com/plamish/xcomfort/issues/46) — won't load on 2025.6.0 (check whether
  PR #47's deprecation fixes already covered this before spending time on it)
- The README's "only devices from one SHC zone" limitation —
  [Connect-Smart/xcomfort_multizone](https://github.com/Connect-Smart/xcomfort_multizone) is 7
  commits ahead of upstream attacking exactly this. Prior art worth reading first.
