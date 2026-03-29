(function () {
  function renderStats(stats) {
    var keys = [
      ["companies_count", "Companies"],
      ["jobs_count", "Jobs"],
      ["active_jobs_count", "Active jobs"],
      ["applications_count", "Applications"],
      ["contacts_count", "Contacts"],
    ];
    var html =
      '<div class="stats-grid">' +
      keys
        .map(function (kv) {
          var v = stats[kv[0]];
          return (
            '<div class="stat"><div class="stat__value">' +
            escapeHtml(String(v != null ? v : "—")) +
            '</div><div class="stat__label">' +
            escapeHtml(kv[1]) +
            "</div></div>"
          );
        })
        .join("") +
      "</div>";
    return html;
  }

  function renderByStatus(rows) {
    if (!rows || !rows.length) {
      return '<p class="empty-state">No applications yet.</p>';
    }
    var h =
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      h +=
        "<tr><td>" +
        escapeHtml(r.status || "—") +
        "</td><td>" +
        escapeHtml(String(r.count)) +
        "</td></tr>";
    });
    h += "</tbody></table></div>";
    return h;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var statsEl = document.getElementById("dashboard-stats");
    var statusEl = document.getElementById("dashboard-by-status");
    clearPageError();
    apiGet("/api/dashboard/stats")
      .then(function (data) {
        statsEl.classList.remove("loading");
        statusEl.classList.remove("loading");
        statsEl.innerHTML = renderStats(data.stats || {});
        statusEl.innerHTML = renderByStatus(data.applications_by_status || []);
      })
      .catch(function (err) {
        statsEl.classList.remove("loading");
        statusEl.classList.remove("loading");
        statsEl.innerHTML = "";
        statusEl.innerHTML = "";
        showPageError(err.message);
      });
  });
})();
