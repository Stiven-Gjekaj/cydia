// Read the Packages file of the repository and group its stanzas by package.

export type Stanza = Record<string, string>;

export interface Version {
  version: string;
  filename: string;
  size: number;
  sha256: string;
}

export interface Package {
  id: string;
  name: string;
  description: string;
  section: string;
  minIOS: string | null;
  homepage: string | null;
  author: string | null;
  icon: string | null;
  // The newest version is first.
  versions: Version[];
}

// Return one record for each stanza. A line that starts with a space or a tab
// continues the field above it.
export function parseStanzas(text: string): Stanza[] {
  const stanzas: Stanza[] = [];
  for (const block of text.split(/\r?\n[ \t]*\r?\n/)) {
    const fields: Stanza = {};
    let key: string | null = null;
    for (const line of block.split(/\r?\n/)) {
      if (/^[ \t]/.test(line) && key) {
        fields[key] += "\n" + line.trim();
      } else {
        const colon = line.indexOf(":");
        if (colon > 0) {
          key = line.slice(0, colon).trim();
          fields[key] = line.slice(colon + 1).trim();
        }
      }
    }
    if (fields.Package) stanzas.push(fields);
  }
  return stanzas;
}

// Compare two versions part by part, so that 0.10.0 is after 0.9.0.
export function compareVersions(a: string, b: string): number {
  const pa = a.split(/[.+~-]/);
  const pb = b.split(/[.+~-]/);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const x = pa[i] ?? "";
    const y = pb[i] ?? "";
    if (x === y) continue;
    const nx = /^\d+$/.test(x);
    const ny = /^\d+$/.test(y);
    if (nx && ny) return Number(x) - Number(y);
    if (x === "") return -1;
    if (y === "") return 1;
    if (nx !== ny) return nx ? -1 : 1;
    return x < y ? -1 : 1;
  }
  return 0;
}

// Return the iOS version in "firmware (>= 6.0)", or null.
export function minIOS(depends: string | undefined): string | null {
  const m = /firmware\s*\(\s*>=\s*([0-9.]+)\s*\)/.exec(depends ?? "");
  return m ? m[1] : null;
}

// Return the name in "Name <mail>", with no mail.
function personName(field: string | undefined): string | null {
  if (!field) return null;
  return field.replace(/\s*<[^>]*>\s*$/, "").trim() || null;
}

export function groupPackages(stanzas: Stanza[]): Package[] {
  const byId = new Map<string, Stanza[]>();
  for (const s of stanzas) {
    const list = byId.get(s.Package) ?? [];
    list.push(s);
    byId.set(s.Package, list);
  }
  const packages: Package[] = [];
  for (const [id, list] of byId) {
    list.sort((a, b) => compareVersions(b.Version, a.Version));
    const newest = list[0];
    packages.push({
      id,
      name: newest.Name ?? id,
      description: newest.Description ?? "",
      section: newest.Section ?? "",
      minIOS: minIOS(newest.Depends),
      homepage: newest.Homepage ?? null,
      author: personName(newest.Author ?? newest.Maintainer),
      icon: newest.Icon ?? null,
      versions: list.map((s) => ({
        version: s.Version,
        filename: s.Filename,
        size: Number(s.Size ?? 0),
        sha256: s.SHA256 ?? "",
      })),
    });
  }
  packages.sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
  return packages;
}

export function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${Math.round(bytes / 1024)} KB`;
}

// Return the first sentence of a description, for a short line on a card.
export function summary(description: string): string {
  const m = /^.*?[.!?](?=\s|$)/s.exec(description.trim());
  return (m ? m[0] : description).trim();
}
