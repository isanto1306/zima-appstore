# iSanto1306 Apps — third-party app store for ZimaOS

A third-party ZimaOS v2 app store for apps maintained by `isanto1306`.

The store currently includes two applications:

- **Disk Monitor** — storage, SMART, temperature, standby, activity and RAID monitoring for ZimaOS/Linux.
- **Update Monitor** — Docker update monitoring with version checks, update policies, targeted checks, backups and restore support.

## Store URL

After GitHub Pages has been deployed from the workflow, add this source in ZimaOS:

`https://isanto1306.github.io/zima-appstore/store.json`

## Available apps

- Disk Monitor
- Update Monitor

## Repository layout

- `Apps/<AppName>/docker-compose.yml`
- `store-config.json`
- `category-list.json`
- `supported-languages.json`
- `.github/workflows/release-store.yml`
- `scripts/build_dist.sh`
