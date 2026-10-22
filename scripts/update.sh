#!/bin/sh
# Make the index of the repository again from the packages in debs/.
# Usage: scripts/update.sh [PACKAGE.deb ...]
# Each package that you give is copied into debs/ first.
set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
for deb in "$@"; do
    cp "$deb" debs/
done

# -m keeps each version of a package, so that a person can go back to one.
dpkg-scanpackages -m debs /dev/null > Packages 2>/dev/null
# The Cydia of iOS 6 reads Packages.bz2 or Packages.gz. Give both.
bzip2 -kf9 Packages
gzip -kf9n Packages

{
    echo "Origin: Stiven"
    echo "Label: Stiven"
    echo "Suite: stable"
    echo "Version: 1.0"
    echo "Codename: ios"
    echo "Architectures: iphoneos-arm"
    echo "Components: main"
    echo "Description: Apps for old iPhones, by Stiven."
    echo "MD5Sum:"
    for file in Packages Packages.bz2 Packages.gz; do
        echo " $(md5 -q "$file") $(wc -c < "$file" | tr -d ' ') $file"
    done
    echo "SHA256:"
    for file in Packages Packages.bz2 Packages.gz; do
        echo " $(shasum -a 256 "$file" | cut -d' ' -f1) $(wc -c < "$file" | tr -d ' ') $file"
    done
} > Release

grep -c '^Package:' Packages | sed 's/$/ packages/'
