(function () {
  var dialog = document.getElementById("company-dialog");
  var form = document.getElementById("company-form");
  var titleEl = document.getElementById("company-dialog-title");

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  }

  function setVal(id, v) {
    var el = document.getElementById(id);
    if (el) el.value = v != null ? String(v) : "";
  }

  function payload() {
    return {
      company_name: val("company_name"),
      industry: val("industry") || null,
      website: val("website") || null,
      city: val("city") || null,
      state: val("state") || null,
      notes: val("notes") || null,
    };
  }

  function openAdd() {
    clearPageError();
    titleEl.textContent = "Add company";
    setVal("company-id", "");
    form.reset();
    dialog.showModal();
  }

  function openEdit(row) {
    clearPageError();
    titleEl.textContent = "Edit company";
    setVal("company-id", row.company_id);
    setVal("company_name", row.company_name);
    setVal("industry", row.industry);
    setVal("website", row.website);
    setVal("city", row.city);
    setVal("state", row.state);
    setVal("notes", row.notes);
    dialog.showModal();
  }

  function renderTable(rows) {
    if (!rows.length) {
      return '<p class="empty-state">No companies yet. Add one to get started.</p>';
    }
    var h =
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Name</th><th>Industry</th><th>Location</th><th></th></tr></thead><tbody>';
    rows.forEach(function (c) {
      var loc = [c.city, c.state].filter(Boolean).join(", ") || "—";
      h +=
        "<tr><td>" +
        escapeHtml(c.company_name) +
        "</td><td>" +
        escapeHtml(c.industry || "—") +
        "</td><td>" +
        escapeHtml(loc) +
        '</td><td class="table-actions"><button type="button" class="btn btn--ghost btn--small btn-edit" data-id="' +
        c.company_id +
        '">Edit</button><button type="button" class="btn btn--danger btn--small btn-del" data-id="' +
        c.company_id +
        '">Delete</button></td></tr>';
    });
    h += "</tbody></table></div>";
    return h;
  }

  function loadList() {
    var container = document.getElementById("companies-container");
    container.classList.add("loading");
    container.textContent = "Loading…";
    return apiGet("/api/companies")
      .then(function (data) {
        container.classList.remove("loading");
        container.innerHTML = renderTable(data.companies || []);
        container.querySelectorAll(".btn-edit").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            apiGet("/api/companies/" + id)
              .then(function (d) {
                openEdit(d.company);
              })
              .catch(function (e) {
                showPageError(e.message);
              });
          });
        });
        container.querySelectorAll(".btn-del").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            if (!confirm("Delete this company? Linked jobs may block this.")) return;
            apiDelete("/api/companies/" + id)
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
    document.getElementById("btn-add-company").addEventListener("click", openAdd);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearPageError();
      var id = val("company-id");
      var p = payload();
      var req = id
        ? apiPut("/api/companies/" + id, p)
        : apiPost("/api/companies", p);
      req
        .then(function () {
          dialog.close();
          loadList();
        })
        .catch(function (err) {
          showPageError(err.message);
        });
    });
    loadList();
  });
})();
