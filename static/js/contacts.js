(function () {
  var dialog = document.getElementById("contact-dialog");
  var form = document.getElementById("contact-form");
  var titleEl = document.getElementById("contact-dialog-title");

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  }

  function setVal(id, v) {
    var el = document.getElementById(id);
    if (el) el.value = v != null ? String(v) : "";
  }

  function fillCompanySelect(companies) {
    var sel = document.getElementById("contact_company_id");
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
      company_id: Number(val("contact_company_id")),
      first_name: val("first_name"),
      last_name: val("last_name"),
      email: val("contact_email") || null,
      phone: val("contact_phone") || null,
      job_title: val("contact_job_title") || null,
      linkedin_url: val("linkedin_url") || null,
      notes: val("contact_notes") || null,
    };
  }

  function openAdd(companies) {
    clearPageError();
    titleEl.textContent = "Add contact";
    setVal("contact-id", "");
    form.reset();
    fillCompanySelect(companies);
    dialog.showModal();
  }

  function openEdit(row, companies) {
    clearPageError();
    titleEl.textContent = "Edit contact";
    setVal("contact-id", row.contact_id);
    fillCompanySelect(companies);
    setVal("contact_company_id", row.company_id);
    setVal("first_name", row.first_name);
    setVal("last_name", row.last_name);
    setVal("contact_email", row.email);
    setVal("contact_phone", row.phone);
    setVal("contact_job_title", row.job_title);
    setVal("linkedin_url", row.linkedin_url);
    setVal("contact_notes", row.notes);
    dialog.showModal();
  }

  function renderTable(rows) {
    if (!rows.length) {
      return '<p class="empty-state">No contacts yet.</p>';
    }
    var h =
      '<div class="table-wrap"><table class="data-table"><thead><tr><th>Name</th><th>Company</th><th>Email</th><th>Title</th><th></th></tr></thead><tbody>';
    rows.forEach(function (c) {
      var name = [c.first_name, c.last_name].filter(Boolean).join(" ");
      h +=
        "<tr><td>" +
        escapeHtml(name) +
        "</td><td>" +
        escapeHtml(c.company_name || "—") +
        "</td><td>" +
        escapeHtml(c.email || "—") +
        "</td><td>" +
        escapeHtml(c.job_title || "—") +
        '</td><td class="table-actions"><button type="button" class="btn btn--ghost btn--small btn-edit" data-id="' +
        c.contact_id +
        '">Edit</button><button type="button" class="btn btn--danger btn--small btn-del" data-id="' +
        c.contact_id +
        '">Delete</button></td></tr>';
    });
    h += "</tbody></table></div>";
    return h;
  }

  var companiesCache = [];

  function loadList() {
    var container = document.getElementById("contacts-container");
    container.classList.add("loading");
    container.textContent = "Loading…";
    return Promise.all([
      apiGet("/api/contacts?detailed=true"),
      apiGet("/api/companies"),
    ])
      .then(function (results) {
        companiesCache = results[1].companies || [];
        container.classList.remove("loading");
        container.innerHTML = renderTable(results[0].contacts || []);
        container.querySelectorAll(".btn-edit").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            apiGet("/api/contacts/" + id + "?detailed=true")
              .then(function (d) {
                openEdit(d.contact, companiesCache);
              })
              .catch(function (e) {
                showPageError(e.message);
              });
          });
        });
        container.querySelectorAll(".btn-del").forEach(function (btn) {
          btn.addEventListener("click", function () {
            var id = btn.getAttribute("data-id");
            if (!confirm("Delete this contact?")) return;
            apiDelete("/api/contacts/" + id)
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
    document.getElementById("btn-add-contact").addEventListener("click", function () {
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
      var id = val("contact-id");
      var p = payload();
      if (!p.company_id) {
        showPageError("Choose a company.");
        return;
      }
      if (!p.first_name || !p.last_name) {
        showPageError("First and last name are required.");
        return;
      }
      var req = id
        ? apiPut("/api/contacts/" + id, p)
        : apiPost("/api/contacts", p);
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
