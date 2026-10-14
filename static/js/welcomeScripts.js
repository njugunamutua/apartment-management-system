// Open / close the About Us and Contact Us popups
function show(id) {
  document.getElementById("aboutForm").style.display = "none";
  document.getElementById("contactForm").style.display = "none";
  document.getElementById(id).style.display = "flex";
}

function openAboutForm()   { show("aboutForm"); }
function openContactForm() { show("contactForm"); }
function closeAboutForm()   { document.getElementById("aboutForm").style.display = "none"; }
function closeContactForm() { document.getElementById("contactForm").style.display = "none"; }

// click the dim background or press Esc to close
document.querySelectorAll(".overlay").forEach(function (o) {
  o.addEventListener("click", function (e) { if (e.target === o) { o.style.display = "none"; } });
});
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") { closeAboutForm(); closeContactForm(); }
});
