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
| `fix/*`, `feat/*` | A change worth offering upstream | Branched off `upstream/master`, kept free of fork-specific commits. |

`main` is the only long-lived branch. The fork's old `master` mirror was deleted on 2026-09-08:
it had drifted 23 commits behind `main`, and work was twice built on it by mistake. Anything meant
to run here starts from `main` — never from `upstream/master`, which `main` has long diverged from.

Keeping the `upstream` remote costs nothing and is the insurance policy: if plamish returns, or if
the integration finds a new home, work can still be offered as a clean PR.

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

**When a change is self-contained enough to offer upstream** — build it off `upstream/master` so
the PR carries none of this fork's own commits, then merge it into `main` to actually use it:

```sh
git fetch upstream
git checkout -b fix/short-description upstream/master
# ...edit, commit...
git push origin fix/short-description
gh pr create --repo plamish/xcomfort --base master --head SEspe:fix/short-description
git checkout main && git merge fix/short-description
```

**If upstream ever moves again:**

```sh
git fetch upstream
git checkout main && git merge upstream/master
```

## Releases

HACS installs from the latest GitHub release, and falls back to the default branch when a
repository has none. Cutting a tag per meaningful change gives HACS a proper update prompt:

```sh
# bump VERSION in custom_components/xcomfort/const.py and "version" in manifest.json together
git tag v1.3.x && git push origin v1.3.x
gh release create v1.3.x --title v1.3.x --notes "..."
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

## Upstream issue status

Fixed in this fork, as of 1.3.13:

- [#48](https://github.com/plamish/xcomfort/issues/48) — binary inputs never appeared; there was
  no `binary_sensor` platform at all. Commented upstream.
- [#32](https://github.com/plamish/xcomfort/issues/32) — humidity, open since Jan 2023 and never
  answered. Commented upstream.
- [#8](https://github.com/plamish/xcomfort/issues/8) — energy/power metering on switching
  actuators, open since Nov 2021. Draft reply written, not posted.
- [#44](https://github.com/plamish/xcomfort/issues/44) — blocking I/O. The live path was already
  fixed upstream in 1.3.6; this fork removed the dead class still carrying it.

Added in this fork without an upstream issue:

- Battery sensors (1.3.13) — one per battery powered physical device, plus the SHC's own
  installation-wide battery summary. The state is the SHC's text (`Good`, …), not a percentage:
  the controller reports battery as a coarse id whose values 1 and 2 both read `Good`, so a
  percentage would be invented precision.

Needs nothing:

- [#46](https://github.com/plamish/xcomfort/issues/46) — fixed upstream in 1.3.7 by PR #47.
- [#26](https://github.com/plamish/xcomfort/issues/26) — scenes are `ButtonEntity` now.
- [#29](https://github.com/plamish/xcomfort/issues/29) — reporter self-resolved.

Out of scope — different hardware:

- [#45](https://github.com/plamish/xcomfort/issues/45) Eaton xStorage,
  [#31](https://github.com/plamish/xcomfort/issues/31) xComfort Bridge (see
  [jankrib/ha-xcomfort-bridge](https://github.com/jankrib/ha-xcomfort-bridge)). Note the remark in
  #31 that Eaton consider the SHC to be nearing end of life, with the Bridge as its successor —
  worth weighing before any large investment here.

Still open and real:

- **`is_connected` is never set to `True`.** The guard in `connect()` therefore always passes, so
  every call re-authenticates against the SHC, including the one `query()` fires on any RPC error.
  Setting it properly is obvious, but it changes runtime behaviour against live hardware and a
  stale session that currently works by brute force could start failing if the flag sticks. Now
  cheap to try, since Reload works. **This is the next thing to look at.**
- **One zone per config entry** — [#30](https://github.com/plamish/xcomfort/issues/30) and
  [#14](https://github.com/plamish/xcomfort/issues/14). The only gap with repeat demand.
  [Connect-Smart/xcomfort_multizone](https://github.com/Connect-Smart/xcomfort_multizone) is 7
  commits ahead of upstream attacking exactly this. Prior art worth reading first.
- **`config_flow.py` does not validate credentials** on the initial setup step, so a wrong
  password only surfaces at entry setup — which now routes into the reauth flow.
