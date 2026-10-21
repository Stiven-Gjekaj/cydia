// Read the packages of the repository at build time.
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { groupPackages, parseStanzas, type Package } from "./packages";

// The site is in site/. The repository files are one directory up.
export const repoRoot = resolve(process.env.REPO_ROOT ?? resolve(process.cwd(), ".."));

export const SOURCE_URL = "https://stiven-gjekaj.github.io/cydia/";
// The links that open the source in each package manager.
export const ADD_LINKS = {
  cydia: `cydia://url/https://cydia.saurik.com/api/share#?source=${SOURCE_URL}`,
  sileo: `sileo://source/${SOURCE_URL}`,
  zebra: `zbra://sources/add/${SOURCE_URL}`,
};
export const GITHUB_URL = "https://github.com/Stiven-Gjekaj/cydia";

let cache: Package[] | null = null;

export function loadPackages(): Package[] {
  cache ??= groupPackages(parseStanzas(readFileSync(resolve(repoRoot, "Packages"), "utf8")));
  return cache;
}

// Return the icon that the control file names, out of the newest .deb.
// Return null if the package has no icon in it.
const icons = new Map<string, Buffer | null>();

export function packageIcon(pkg: Package): Buffer | null {
  if (!icons.has(pkg.id)) icons.set(pkg.id, readIcon(pkg));
  return icons.get(pkg.id) ?? null;
}

function readIcon(pkg: Package): Buffer | null {
  if (!pkg.icon?.startsWith("file://")) return null;
  const deb = resolve(repoRoot, pkg.versions[0].filename);
  if (!existsSync(deb)) return null;
  const member = "." + pkg.icon.slice("file://".length);
  try {
    const tar = execFileSync("dpkg-deb", ["--fsys-tarfile", deb], { maxBuffer: 1 << 30 });
    const data = execFileSync("tar", ["-xOf", "-", member], { input: tar, maxBuffer: 1 << 26 });
    return data.length > 0 ? data : null;
  } catch {
    return null;
  }
}
