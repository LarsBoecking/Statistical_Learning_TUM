/* ---------------------------------------------------------------------------
 * ONE PLACE TO EDIT for repository links.
 * The site is published from two repositories. Each deployment links to its
 * own repository, detected from the host name the page is served from.
 * Every "View slides" / "Open notebook" / figure link on the site is built
 * from these values, so you never have to touch the HTML.
 * ------------------------------------------------------------------------- */
const SITE_DEFAULT = {
  user: "LarsBoecking",
  repo: "Statistical_Learning_TUM",
  branch: "main",
};

/* Host name -> overrides. Add an entry for every additional deployment. */
const SITE_DEPLOYMENTS = {
  "ishumancentricai.github.io": { user: "ishumancentricai", repo: "tum-statistical-learning" },
};

window.SITE = Object.assign({}, SITE_DEFAULT, SITE_DEPLOYMENTS[window.location.hostname] || {});

/* Build repository URLs from a path relative to the repo root. */
window.repoLink = function (path, kind) {
  const s = window.SITE;
  const p = path.split("/").map(encodeURIComponent).join("/");
  if (kind === "raw") {
    return `https://raw.githubusercontent.com/${s.user}/${s.repo}/${s.branch}/${p}`;
  }
  // default: GitHub blob view (renders PDFs and notebooks in the browser)
  return `https://github.com/${s.user}/${s.repo}/blob/${s.branch}/${p}`;
};

/* Resolve every <a data-file="..." data-kind="blob|raw"> on the page. */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("a[data-file]").forEach(function (a) {
    a.href = window.repoLink(a.getAttribute("data-file"), a.getAttribute("data-kind") || "blob");
    if ((a.getAttribute("data-kind") || "blob") === "blob") {
      a.target = "_blank";
      a.rel = "noopener";
    }
  });
  // Fill any element tagged data-repo-home with the repo root URL.
  const s = window.SITE;
  document.querySelectorAll("a[data-repo-home]").forEach(function (a) {
    a.href = `https://github.com/${s.user}/${s.repo}`;
  });
  // Fill any element tagged data-clone-cmd with the matching clone command.
  document.querySelectorAll("[data-clone-cmd]").forEach(function (el) {
    el.textContent = `git clone https://github.com/${s.user}/${s.repo}.git && cd ${s.repo}`;
  });
});
