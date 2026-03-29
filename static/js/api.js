/**
 * JSON fetch helpers for the Job Application Tracker API.
 * Same-origin requests; no flash UI — callers handle errors via showPageError.
 */
(function () {
  async function parseBody(res) {
    const text = await res.text();
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return { _raw: text };
    }
  }

  window.apiCall = async function (path, options) {
    options = options || {};
    const headers = Object.assign({}, options.headers);
    let body = options.body;
    if (body != null && typeof body === "object" && !(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(body);
    }
    const res = await fetch(path, Object.assign({}, options, { headers, body }));
    const data = await parseBody(res);
    if (!res.ok) {
      const msg = data.error || data.message || res.statusText || "Request failed";
      throw new Error(msg);
    }
    return data;
  };

  window.apiGet = (path) => window.apiCall(path, { method: "GET" });
  window.apiPost = (path, body) => window.apiCall(path, { method: "POST", body });
  window.apiPut = (path, body) => window.apiCall(path, { method: "PUT", body });
  window.apiDelete = (path) => window.apiCall(path, { method: "DELETE" });
})();
