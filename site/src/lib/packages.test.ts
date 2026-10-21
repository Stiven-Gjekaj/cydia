import { describe, expect, it } from "vitest";
import {
  compareVersions,
  formatSize,
  groupPackages,
  minIOS,
  parseStanzas,
  summary,
} from "./packages";

const text = [
  "Package: com.example.b",
  "Version: 0.9.0",
  "Filename: debs/b_0.9.0.deb",
  "Size: 2048",
  "Name: Beta",
  "",
  "Package: com.example.b",
  "Version: 0.10.0",
  "Filename: debs/b_0.10.0.deb",
  "Size: 3145728",
  "Name: Beta",
  "Description: First line",
  " second line",
  "Depends: firmware (>= 6.0)",
  "Author: Some Person <person@example.com>",
  "",
  "",
  "Package: com.example.a",
  "Version: 1.0",
  "Filename: debs/a_1.0.deb",
  "Size: 100",
  "Name: alpha",
  "",
].join("\n");

describe("parseStanzas", () => {
  it("reads each stanza and joins continuation lines", () => {
    const stanzas = parseStanzas(text);
    expect(stanzas).toHaveLength(3);
    expect(stanzas[1].Description).toBe("First line\nsecond line");
  });

  it("reads a file with CRLF line ends", () => {
    expect(parseStanzas(text.replace(/\n/g, "\r\n"))).toHaveLength(3);
  });
});

describe("compareVersions", () => {
  it("compares numbers, not text", () => {
    expect(compareVersions("0.10.0", "0.9.0")).toBeGreaterThan(0);
    expect(compareVersions("1.0", "1.0.1")).toBeLessThan(0);
    expect(compareVersions("1.2.0", "1.2.0")).toBe(0);
  });
});

describe("groupPackages", () => {
  const packages = groupPackages(parseStanzas(text));

  it("sorts the packages by name with no case", () => {
    expect(packages.map((p) => p.name)).toEqual(["alpha", "Beta"]);
  });

  it("puts the newest version first and reads its fields", () => {
    const beta = packages[1];
    expect(beta.versions.map((v) => v.version)).toEqual(["0.10.0", "0.9.0"]);
    expect(beta.minIOS).toBe("6.0");
    expect(beta.author).toBe("Some Person");
    expect(beta.versions[0].size).toBe(3145728);
  });

  it("gives null for a field that is not there", () => {
    expect(packages[0].minIOS).toBeNull();
    expect(packages[0].homepage).toBeNull();
  });
});

describe("minIOS and formatSize", () => {
  it("reads the firmware version with any spaces", () => {
    expect(minIOS("firmware(>=7.0)")).toBe("7.0");
    expect(minIOS("mobilesubstrate")).toBeNull();
  });

  it("gives KB and MB", () => {
    expect(formatSize(2048)).toBe("2 KB");
    expect(formatSize(3145728)).toBe("3.0 MB");
  });
});

describe("summary", () => {
  it("gives the first sentence", () => {
    expect(summary("A demake of Balatro for iOS 6. It needs a file.")).toBe("A demake of Balatro for iOS 6.");
  });

  it("does not stop at a dot inside a word", () => {
    expect(summary("It needs Balatro.love to run. More.")).toBe("It needs Balatro.love to run.");
  });

  it("gives all the text when it has no full stop", () => {
    expect(summary("A player")).toBe("A player");
  });
});
