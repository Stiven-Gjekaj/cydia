# Cydia repository of Stiven Gjekaj

Apps for old iPhones on a jailbreak. The first one is
[RetroTube](https://github.com/Stiven-Gjekaj/RetroTube), a YouTube client for
iOS 6.

## Add the repository

> [!IMPORTANT]
> **Cydia on iOS 6 cannot read this repository.** GitHub Pages accepts only
> TLS 1.2, and the APT of iOS 6 Cydia stops at TLS 1.0 (SSL error -9836).
> GitHub also does not serve plain HTTP on `github.io`. On iOS 6, download
> the `.deb` from the release of the app and install it with `dpkg -i`.
> The repository works with iOS 7 and later, and with an APT that has
> TLS 1.2.

1. Open Cydia.
2. Tap Sources, then Edit, then Add.
3. Type `https://stiven-gjekaj.github.io/cydia/` and tap Add Source.

Or, on the phone, open
[this link](cydia://url/https://cydia.saurik.com/api/share#?source=https://stiven-gjekaj.github.io/cydia/)
in Safari.

With APT on the command line, add this line to a file in
`/etc/apt/sources.list.d/`:

```
deb https://stiven-gjekaj.github.io/cydia/ ./
```

## Packages

| Package | Version | For |
| ------- | ------- | --- |
| RetroTube (`io.github.stivengjekaj.retrotube`) | 1.0.0 | iOS 6 or newer |

## Add a package

```
scripts/update.sh path/to/package.deb
```

The script copies the package into `debs/` and makes `Packages`,
`Packages.bz2`, `Packages.gz`, and `Release` again. Commit the result and
push it. GitHub Pages serves the `main` branch.

The repository keeps each version of a package in `debs/`.
The `Release` file has no signature. Cydia accepts a repository with no
signature.
