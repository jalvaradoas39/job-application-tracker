(function () {
  function parseSkills(text) {
    return text
      .split(/[\n,]+/)
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("btn-run-match");
    var input = document.getElementById("skills-input");
    var results = document.getElementById("match-results");
    var wrap = document.getElementById("match-table-wrap");

    btn.addEventListener("click", function () {
      clearPageError();
      var skills = parseSkills(input.value);
      if (!skills.length) {
        showPageError("Enter at least one skill.");
        results.hidden = true;
        return;
      }
      btn.disabled = true;
      wrap.innerHTML = '<p class="loading">Matching…</p>';
      results.hidden = false;
      apiPost("/api/job-match", { skills: skills })
        .then(function (data) {
          btn.disabled = false;
          var rows = data.matches || [];
          if (!rows.length) {
            wrap.innerHTML =
              '<p class="empty-state">No active jobs to compare.</p>';
            return;
          }
          var h =
            '<div class="table-wrap"><table class="data-table"><thead><tr><th>Match</th><th>Job</th><th>Company</th><th>Skills</th></tr></thead><tbody>';
          rows.forEach(function (m) {
            var pct = m.match_percent;
            var bar =
              '<div class="match-bar" aria-hidden="true"><div class="match-bar__fill" style="width:' +
              Math.min(100, pct) +
              '%"></div></div>';
            h +=
              "<tr><td>" +
              bar +
              " <strong>" +
              escapeHtml(String(pct)) +
              "%</strong><br><span class=\"hint\">" +
              escapeHtml(String(m.matched_skills)) +
              "/" +
              escapeHtml(String(m.user_skills_count)) +
              "</span></td><td>" +
              escapeHtml(m.job_title) +
              "</td><td>" +
              escapeHtml(m.company_name || "—") +
              "</td><td><small>" +
              escapeHtml((m.job_requirements_parsed || []).join(", ") || "—") +
              "</small></td></tr>";
          });
          h += "</tbody></table></div>";
          wrap.innerHTML = h;
        })
        .catch(function (e) {
          btn.disabled = false;
          wrap.innerHTML = "";
          results.hidden = true;
          showPageError(e.message);
        });
    });
  });
})();
