(function () {
  var dialog = document.getElementById("job-dialog");
  var form = document.getElementById("job-form");
  var titleEl = document.getElementById("job-dialog-title");

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  }

  function setVal(id, v) {
    var el = document.getElementById(id);
    if (el) el.value = v != null ? String(v) : "";
  }

  function parseJsonField(text, label) {
    var t = (text || "").trim();
    if (!t) return null;
    try {
      return JSON.parse(t);
    } catch (e) {
      throw new Error(label + ": invalid JSON — " + e.message);
    }
  }

  function numOrNull(id) {
    var v = val(id);
    if (!v) return null;
    var n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function fillCompanySelect(companies) {
    var sel = document.getElementById("job_company_id");
    sel.innerHTML =
      '<option value="">Select company…</option>' +
      (companies || [])
        .map(function (c) {
          return (
            '<option value="' +
            c.company_id +
            '">' +
            escapeHtml(c.company_name) +
            "</option>"
          );
        })
        .join("");
  }

  function payload() {
    return {
      company_id: Number(val("job_company_id")),
      job_title: val("job_title"),
      job_description: val("job_description") || null,
      salary_min: numOrNull("salary_min"),
      salary_max: numOrNull("salary_max"),
      job_type: val("job_type") || null,
      posting_url: val("posting_url") || null,
      date_posted: val("date_posted") || null,
      is_active: document.getElementById("is_active").checked,
      requirements: parseJsonField(val("requirements"), "Requirements"),
    };
  }

  function openAdd(companies) {
    clearPageError();
    titleEl.textContent = "Add job";
    setVal("job-id", "");
    form.reset();
    document.getElementById("is_active").checked = true;
    fillCompanySelect(companies);
    dialog.showModal();
  }

  function openEdit(row, companies) {
    clearPageError();
    titleEl.textContent = "Edit job";
    setVal("job-id", row.job_id);
    fillCompanySelect(companies);
    setVal("job_company_id", row.company_id);
    setVal("job_title", row.job_title);
    setVal("job_description", row.job_description);
    setVal("salary_min", row.salary_min);
    setVal("salary_max", row.salary_max);
    setVal("job_type", row.job_type);
    setVal("posting_url", row.posting_url);
    setVal("date_posted", row.date_posted || "");
    document.getElementById("is_active").checked =
      row.is_active === true ||
      row.is_active === 1 ||
      row.is_active === "1";
    var req = row.requirements;
    setVal(
      "requirements",
      req != null
        ? typeof req === "string"
          ? req
          : JSON.stringify(req, null, 2)
        : ""
    );
    dialog.showModal();
  }

  function renderTable(rows) {
    if (!rows.length) {
      return '<p class="empty-state">No jobs yet.</p>';
    }
    var h =
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Title</th><th>Company</th><th>Type</th><th>Salary</th><th>Active</th><th></th></tr></thead><tbody>';
    rows.forEach(function (j) {
      var sal =
        formatMoney(j.salary_min) + " – " + formatMoney(j.salary_max);
      var active =
        j.is_active === true || j.is_active === 1 ? "Yes" : "No";
      h +=
        "<tr><td>" +
        escapeHtml(j.job_title) +
        "</td><td>" +
        escapeHtml(j.company_name || "—") +
        "</td><td>" +
        escapeHtml(j.job_type || "—") +
        "</td><td>" +
        escapeHtml(sal) +
        "</td><td>" +
        escapeHtml(active) +
        '</td><td class="table-actions"><button type="button" class="btn btn--ghost btn--small btn-edit" data-id="' +
        j.job_id +
        '">Edit</button><button type="button" class="btn btn--danger btn--small btn-del" data-id="' +
        j.job_id +
        '">Delete</button></td></tr>';
    });
    h += "</tbody></table></div>";
    return h;
  }

  var companiesCache = [];

  function loadList() {
    var container = document.getElementById("jobs-container");
    container.classList.add("loading");
    container.textContent = "Loading…";
    return Promise.all([
      apiGet("/api/jobs?detailed=true"),
      apiGet("/api/companies"),
    ])
      .then(function (results) {
        companiesCache = results[1].companies || [];
        container.classList.remove("loading");
        container.innerHTML = renderTable(results[0].jobs || []);
        container.querySelectorAll(".btn-edit").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            apiGet("/api/jobs/" + id + "?detailed=true")
              .then(function (d) {
                openEdit(d.job, companiesCache);
              })
              .catch(function (e) {
                showPageError(e.message);
              });
          });
        });
        container.querySelectorAll(".btn-del").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            if (!confirm("Delete this job? Applications may block this."))
              return;
            apiDelete("/api/jobs/" + id)
              .then(function () {
                clearPageError();
                loadList();
              })
              .catch(function (e) {
                showPageError(e.message);
              });
          });
        });
      })
      .catch(function (e) {
        container.classList.remove("loading");
        container.innerHTML = "";
        showPageError(e.message);
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("btn-add-job").addEventListener("click", function () {
      apiGet("/api/companies")
        .then(function (d) {
          companiesCache = d.companies || [];
          openAdd(companiesCache);
        })
        .catch(function (e) {
          showPageError(e.message);
        });
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearPageError();
      var id = val("job-id");
      try {
        var p = payload();
        if (!p.company_id) throw new Error("Choose a company.");
        if (!p.job_title) throw new Error("Job title is required.");
        var req = id
          ? apiPut("/api/jobs/" + id, p)
          : apiPost("/api/jobs", p);
        req
          .then(function () {
            dialog.close();
            loadList();
          })
          .catch(function (err) {
            showPageError(err.message);
          });
      } catch (err) {
        showPageError(err.message);
      }
    });
    loadList();
  });
})();
