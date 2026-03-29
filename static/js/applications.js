(function () {
  var dialog = document.getElementById("application-dialog");
  var form = document.getElementById("application-form");
  var titleEl = document.getElementById("application-dialog-title");

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

  function toDatetimeLocal(mysqlDt) {
    if (!mysqlDt) return "";
    var s = String(mysqlDt).replace(" ", "T");
    if (s.length >= 16) return s.slice(0, 16);
    return s;
  }

  function fromDatetimeLocal(v) {
    if (!v) return null;
    if (v.length === 16) return v.replace("T", " ") + ":00";
    return v.replace("T", " ");
  }

  function fillJobSelect(jobs) {
    var sel = document.getElementById("app_job_id");
    sel.innerHTML =
      '<option value="">Select job…</option>' +
      (jobs || [])
        .map(function (j) {
          var label =
            escapeHtml(j.job_title) +
            " · " +
            escapeHtml(j.company_name || "");
          return (
            '<option value="' + j.job_id + '">' + label + "</option>"
          );
        })
        .join("");
  }

  function payload() {
    return {
      job_id: Number(val("app_job_id")),
      application_date: val("application_date"),
      status: val("app_status") || "Applied",
      resume_version: val("resume_version") || null,
      cover_letter_sent: document.getElementById("cover_letter_sent").checked,
      response_date: val("response_date") || null,
      interview_date: fromDatetimeLocal(val("interview_date")),
      notes: val("app_notes") || null,
      interview_data: parseJsonField(val("interview_data"), "Interview data"),
    };
  }

  function openAdd(jobs) {
    clearPageError();
    titleEl.textContent = "Add application";
    setVal("application-id", "");
    form.reset();
    fillJobSelect(jobs);
    dialog.showModal();
  }

  function openEdit(row, jobs) {
    clearPageError();
    titleEl.textContent = "Edit application";
    setVal("application-id", row.application_id);
    fillJobSelect(jobs);
    setVal("app_job_id", row.job_id);
    setVal("application_date", row.application_date || "");
    setVal("app_status", row.status || "");
    setVal("resume_version", row.resume_version);
    document.getElementById("cover_letter_sent").checked =
      row.cover_letter_sent === true ||
      row.cover_letter_sent === 1 ||
      row.cover_letter_sent === "1";
    setVal("response_date", row.response_date || "");
    setVal("interview_date", toDatetimeLocal(row.interview_date));
    setVal("app_notes", row.notes);
    var idata = row.interview_data;
    setVal(
      "interview_data",
      idata != null
        ? typeof idata === "string"
          ? idata
          : JSON.stringify(idata, null, 2)
        : ""
    );
    dialog.showModal();
  }

  function renderTable(rows) {
    if (!rows.length) {
      return '<p class="empty-state">No applications yet.</p>';
    }
    var h =
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Job</th><th>Company</th><th>Date</th><th>Status</th><th></th></tr></thead><tbody>';
    rows.forEach(function (a) {
      h +=
        "<tr><td>" +
        escapeHtml(a.job_title || "—") +
        "</td><td>" +
        escapeHtml(a.company_name || "—") +
        "</td><td>" +
        escapeHtml(a.application_date || "—") +
        "</td><td>" +
        escapeHtml(a.status || "—") +
        '</td><td class="table-actions"><button type="button" class="btn btn--ghost btn--small btn-edit" data-id="' +
        a.application_id +
        '">Edit</button><button type="button" class="btn btn--danger btn--small btn-del" data-id="' +
        a.application_id +
        '">Delete</button></td></tr>';
    });
    h += "</tbody></table></div>";
    return h;
  }

  var jobsCache = [];

  function loadList() {
    var container = document.getElementById("applications-container");
    container.classList.add("loading");
    container.textContent = "Loading…";
    return Promise.all([
      apiGet("/api/applications?detailed=true"),
      apiGet("/api/jobs?detailed=true"),
    ])
      .then(function (results) {
        jobsCache = results[1].jobs || [];
        container.classList.remove("loading");
        container.innerHTML = renderTable(results[0].applications || []);
        container.querySelectorAll(".btn-edit").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            apiGet("/api/applications/" + id + "?detailed=true")
              .then(function (d) {
                openEdit(d.application, jobsCache);
              })
              .catch(function (e) {
                showPageError(e.message);
              });
          });
        });
        container.querySelectorAll(".btn-del").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            if (!confirm("Delete this application?")) return;
            apiDelete("/api/applications/" + id)
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
    document
      .getElementById("btn-add-application")
      .addEventListener("click", function () {
        apiGet("/api/jobs?detailed=true")
          .then(function (d) {
            jobsCache = d.jobs || [];
            openAdd(jobsCache);
          })
          .catch(function (e) {
            showPageError(e.message);
          });
      });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearPageError();
      var id = val("application-id");
      try {
        var p = payload();
        if (!p.job_id) throw new Error("Choose a job.");
        if (!p.application_date) throw new Error("Application date is required.");
        var req = id
          ? apiPut("/api/applications/" + id, p)
          : apiPost("/api/applications", p);
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
