(function () {
  window.showPageError = function (message) {
    var el = document.getElementById("page-error");
    if (!el) return;
    el.textContent = message || "";
    el.hidden = !message;
    el.setAttribute("aria-live", "polite");
  };

  window.clearPageError = function () {
    window.showPageError("");
  };

  window.escapeHtml = function (s) {
    if (s == null) return "";
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  };

  window.formatMoney = function (n) {
    if (n == null || n === "") return "—";
    var x = Number(n);
    if (Number.isNaN(x)) return String(n);
    return (
      "$" +
      x.toLocaleString(undefined, { maximumFractionDigits: 0 })
    );
  };

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-close");
        var dlg = document.getElementById(id);
        if (dlg && typeof dlg.close === "function") dlg.close();
      });
    });
  });
})();
