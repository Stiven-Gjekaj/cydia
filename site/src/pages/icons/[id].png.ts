// Write the icon of each package to icons/<id>.png.
import type { APIRoute, GetStaticPaths } from "astro";
import { loadPackages, packageIcon } from "../../lib/repo";

export const getStaticPaths = (() =>
  loadPackages()
    .map((pkg) => ({ pkg, icon: packageIcon(pkg) }))
    .filter(({ icon }) => icon !== null)
    .map(({ pkg, icon }) => ({ params: { id: pkg.id }, props: { icon } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
  new Response(new Uint8Array(props.icon as Buffer), { headers: { "Content-Type": "image/png" } });
