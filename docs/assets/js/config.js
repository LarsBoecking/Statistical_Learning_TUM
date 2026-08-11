/* ---------------------------------------------------------------------------
 * ONE PLACE TO EDIT after you create the GitHub repository.
 * Set your GitHub username, the repository name, and the default branch.
 * Every "View slides" / "Open notebook" / figure link on the site is built
 * from these three values, so you never have to touch the HTML.
 * ------------------------------------------------------------------------- */
window.SITE = {
  user: "LarsBoecking",
  repo: "Statistical_Learning_TUM",
  branch: "main",
};

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
});
