#!/usr/bin/env python3
"""Make index.html and icons/ from the Packages file of the repository.

Usage: scripts/page.py

The page lists each package with its latest version, a link to its .deb,
and its old versions. The Safari of iOS 6 shows the page, so the page uses
no script and only old CSS.
"""
import html
import io
import os
import re
import subprocess
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = "https://stiven-gjekaj.github.io/cydia/"
ADD_LINK = "cydia://url/https://cydia.saurik.com/api/share#?source=" + SOURCE


def read_packages(path):
    """Return one dict for each stanza in a Packages file."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    stanzas = []
    for block in re.split(r"\n\s*\n", text):
        fields = {}
        key = None
        for line in block.splitlines():
            if line[:1] in (" ", "\t") and key:
                fields[key] += "\n" + line.strip()
            elif ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                fields[key] = value.strip()
        if "Package" in fields:
            stanzas.append(fields)
    return stanzas


def version_key(version):
    """Sort a version by its numbers, so that 0.10.0 is after 0.9.0."""
    return [(0, int(p), "") if p.isdigit() else (1, 0, p)
            for p in re.split(r"[.+~-]", version)]


def group(stanzas):
    """Return a list of (package id, versions with the newest first)."""
    by_id = {}
    for s in stanzas:
        by_id.setdefault(s["Package"], []).append(s)
    groups = []
    for pid, versions in by_id.items():
        versions.sort(key=lambda s: version_key(s["Version"]), reverse=True)
        groups.append((pid, versions))
    groups.sort(key=lambda g: g[1][0].get("Name", g[0]).lower())
    return groups


def extract_icon(deb_path, icon_url, out_path):
    """Copy the icon that the control file names out of the .deb.

    Return True if the icon is in the package.
    """
    if not icon_url.startswith("file://"):
        return False
    member = "." + icon_url[len("file://"):]
    try:
        tar_bytes = subprocess.run(
            ["dpkg-deb", "--fsys-tarfile", deb_path],
            check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return False
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
        try:
            data = tar.extractfile(member)
        except KeyError:
            return False
        if data is None:
            return False
        with open(out_path, "wb") as out:
            out.write(data.read())
    return True


def size_text(size):
    size = int(size)
    if size >= 1024 * 1024:
        return "%.1f MB" % (size / 1024 / 1024)
    return "%d KB" % round(size / 1024)


def firmware_text(depends):
    m = re.search(r"firmware \(>= ([0-9.]+)\)", depends or "")
    return "iOS %s or newer" % m.group(1) if m else "Any iOS"


def card(pid, versions, icon):
    e = html.escape
    new = versions[0]
    name = new.get("Name", pid)
    out = ['<div class="card" id="%s">' % e(pid)]
    out.append('<div class="head">')
    if icon:
        out.append('<img class="icon" src="%s" width="57" height="57" alt="">'
                   % e(icon))
    else:
        out.append('<div class="icon blank"></div>')
    out.append('<div class="title"><h2>%s</h2>' % e(name))
    out.append('<p class="meta">%s &middot; %s</p></div></div>'
               % (e(new.get("Section", "")), e(firmware_text(new.get("Depends")))))
    out.append('<p>%s</p>' % e(new.get("Description", "")))
    out.append('<table class="facts">')
    out.append('<tr><th>Version</th><td>%s</td></tr>' % e(new["Version"]))
    out.append('<tr><th>Size</th><td>%s</td></tr>' % e(size_text(new["Size"])))
    out.append('<tr><th>Package</th><td><code>%s</code></td></tr>' % e(pid))
    out.append('</table>')
    out.append('<div class="links">')
    out.append('<a class="button" href="%s">Download %s</a>'
               % (e(new["Filename"]), e(new["Version"])))
    if new.get("Homepage"):
        out.append('<a class="button light" href="%s">Source code</a>'
                   % e(new["Homepage"]))
    out.append('</div>')
    if len(versions) > 1:
        out.append('<details><summary>Old versions (%d)</summary><ul class="old">'
                   % (len(versions) - 1))
        for v in versions[1:]:
            out.append('<li><a href="%s">%s</a> <span>%s</span></li>'
                       % (e(v["Filename"]), e(v["Version"]),
                          e(size_text(v["Size"]))))
        out.append('</ul></details>')
    out.append('</div>')
    return "\n".join(out)


STYLE = """
:root { color-scheme: light dark; }
body { margin: 0; padding: 0; background: #f4e9cf; color: #3a1f0d;
       font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 16px;
       line-height: 1.45; -webkit-text-size-adjust: 100%; }
.wrap { max-width: 720px; margin: 0 auto; padding: 0 16px 32px; }
header { text-align: center; padding: 28px 0 8px; }
header img { border-radius: 14px; }
h1 { font-size: 26px; margin: 10px 0 4px; }
.lead { margin: 0 0 8px; color: #6b4a33; }
h2 { font-size: 20px; margin: 0; }
h3 { font-size: 17px; margin: 28px 0 8px; }
a { color: #8a4b1f; }
code { background: #fff8e8; border: 1px solid #e3d2ad; border-radius: 4px;
       padding: 1px 5px; font-size: 14px; word-break: break-all; }
.box { background: #fffaf0; border: 1px solid #e3d2ad; border-radius: 12px;
       padding: 14px 16px; margin: 16px 0; }
.note { background: #fbeccb; border-color: #d8b469; }
.note strong { color: #7a3d0c; }
.button { display: block; margin: 10px 0 0; padding: 12px; text-align: center;
          background: #6b3d20; color: #f4e9cf; text-decoration: none;
          border-radius: 9px; font-weight: bold;
          -webkit-box-sizing: border-box; box-sizing: border-box; }
.button.light { background: #fff8e8; color: #6b3d20; border: 1px solid #c9a982; }
.card { background: #fffaf0; border: 1px solid #e3d2ad; border-radius: 14px;
        padding: 16px; margin: 16px 0; }
.head { overflow: hidden; }
.icon { float: left; width: 57px; height: 57px; border-radius: 12px;
        margin-right: 14px; }
.icon.blank { background: #e3d2ad; }
.title { overflow: hidden; padding-top: 6px; }
.meta { margin: 2px 0 0; color: #8a6a50; font-size: 14px; }
.facts { border-collapse: collapse; width: 100%; font-size: 15px; }
.facts th { text-align: left; font-weight: normal; color: #8a6a50;
            width: 90px; padding: 3px 0; vertical-align: top; }
.facts td { padding: 3px 0; }
details { margin-top: 12px; font-size: 15px; }
summary { cursor: pointer; color: #8a4b1f; }
.old { margin: 8px 0 0; padding-left: 20px; }
.old span { color: #8a6a50; font-size: 14px; }
pre { background: #fff8e8; border: 1px solid #e3d2ad; border-radius: 8px;
      padding: 10px; overflow-x: auto; font-size: 14px; }
footer { text-align: center; color: #8a6a50; font-size: 14px; margin-top: 32px; }
@media (min-width: 600px) {
  .links { overflow: hidden; }
  .links .button { float: left; width: 48%; margin-right: 4%; }
  .links .button:last-child { margin-right: 0; }
}
@media (prefers-color-scheme: dark) {
  body { background: #1f140c; color: #f0e2c4; }
  .lead, .meta, .facts th, .old span, footer { color: #b8987a; }
  a, summary { color: #e0a56f; }
  .box, .card { background: #2b1c11; border-color: #4a3220; }
  .note { background: #3a2410; border-color: #7a5428; }
  .note strong { color: #f0b46a; }
  code, pre { background: #1a100a; border-color: #4a3220; }
  .button { background: #d9a066; color: #1f140c; }
  .button.light { background: #2b1c11; color: #e0a56f; border-color: #6b4a33; }
  .icon.blank { background: #4a3220; }
}
"""


def page(groups, icons):
    e = html.escape
    cards = "\n".join(card(pid, versions, icons.get(pid))
                      for pid, versions in groups)
    count = len(groups)
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stiven Gjekaj Cydia Repository</title>
<link rel="apple-touch-icon" href="CydiaIcon.png">
<link rel="icon" href="CydiaIcon.png">
<style>%(style)s</style>
</head>
<body>
<!-- scripts/page.py makes this file. Do not edit it. -->
<div class="wrap">
<header>
<img src="CydiaIcon.png" width="64" height="64" alt="">
<h1>Stiven Gjekaj</h1>
<p class="lead">%(count)d apps for old iPhones on a jailbreak.</p>
</header>

<a class="button" href="%(add)s">Add to Cydia</a>
<div class="box">
<p style="margin-top:0">Or add this source in Cydia, Sileo, or Zebra:</p>
<p><code>%(source)s</code></p>
<p style="margin-bottom:0">With APT, put this line in a file in <code>/etc/apt/sources.list.d/</code>:</p>
<pre>deb %(source)s ./</pre>
</div>

<div class="box note">
<p style="margin:0"><strong>On iOS 6, Cydia cannot read this source.</strong>
GitHub Pages accepts only TLS 1.2, and the APT of iOS 6 stops at TLS 1.0.
On iOS 6, download the <code>.deb</code> below and install it with
<code>dpkg -i</code>, or with an app that installs a <code>.deb</code> file.
The source works with iOS 7 and later.</p>
</div>

<h3>Packages</h3>
%(cards)s

<footer>
<p>Each version of each package stays in the repository.<br>
<a href="https://github.com/Stiven-Gjekaj/cydia">Repository on GitHub</a></p>
</footer>
</div>
</body>
</html>
""" % {"style": STYLE, "count": count, "add": e(ADD_LINK),
       "source": e(SOURCE), "cards": cards}


def main():
    groups = group(read_packages(os.path.join(ROOT, "Packages")))
    icon_dir = os.path.join(ROOT, "icons")
    os.makedirs(icon_dir, exist_ok=True)
    icons = {}
    for pid, versions in groups:
        new = versions[0]
        rel = "icons/%s.png" % pid
        if extract_icon(os.path.join(ROOT, new["Filename"]),
                        new.get("Icon", ""), os.path.join(ROOT, rel)):
            icons[pid] = rel
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(groups, icons))
    print("%d packages on the page" % len(groups))


if __name__ == "__main__":
    sys.exit(main())
