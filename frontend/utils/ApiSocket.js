const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
  throw new Error("VITE_API_BASE_URL is not defined in .env");
}

// helper to read cookie
const getCookie = (name) => {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
};

const defaultHeaders = {
  "Content-Type": "application/json",
};

const handleResponse = async (res) => {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const error = data?.error || `HTTP ${res.status}`;
    throw new Error(error);
  }
  return data;
};

const ApiSocket = {
  get: async (endpoint) => {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "GET",
      headers: defaultHeaders,
      credentials: "include",
    });
    return handleResponse(res);
  },

  post: async (endpoint, body) => {
    const csrfToken = getCookie("csrf_token");
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        ...defaultHeaders,
        "X-CSRF-Token": csrfToken || "",
      },
      credentials: "include",
      body: JSON.stringify(body),
    });
    return handleResponse(res);
  },

  put: async (endpoint, body) => {
    const csrfToken = getCookie("csrf_token");
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "PUT",
      headers: {
        ...defaultHeaders,
        "X-CSRF-Token": csrfToken || "",
      },
      credentials: "include",
      body: JSON.stringify(body),
    });
    return handleResponse(res);
  },

  delete: async (endpoint) => {
    const csrfToken = getCookie("csrf_token");
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "DELETE",
      headers: {
        ...defaultHeaders,
        "X-CSRF-Token": csrfToken || "",
      },
      credentials: "include",
    });
    return handleResponse(res);
  },
};

export default ApiSocket;
