/* Landing page: the large hero logos shrink into the sticky header on scroll.
   On other pages (no #hero-logos) the header logos are simply always shown. */
document.addEventListener("DOMContentLoaded", function () {
  var hero = document.getElementById("hero-logos");
  var hdr = document.querySelector(".hdr");
  if (!hdr) return;
  if (!hero) { hdr.classList.add("show-logos"); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      hdr.classList.toggle("show-logos", !e.isIntersecting);
    });
  }, { rootMargin: "-64px 0px 0px 0px", threshold: 0 });
  io.observe(hero);
});
