const CANONICAL_HOST = "cluesbysam.net";

function redirect(url) {
  return Response.redirect(url.toString(), 308);
}

function withHeaders(response, hostname) {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  if (hostname.endsWith(".workers.dev")) {
    headers.set("X-Robots-Tag", "noindex");
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

function assetRequest(request, pathname) {
  const url = new URL(request.url);
  url.pathname = pathname;
  return new Request(url, request);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname === `www.${CANONICAL_HOST}`) {
      url.hostname = CANONICAL_HOST;
      return redirect(url);
    }

    if (url.pathname === "/index.html") {
      url.pathname = "/";
      return redirect(url);
    }

    const levelIndex = url.pathname.match(/^\/level\/([^/]+)\/index\.html$/);
    if (levelIndex) {
      url.pathname = `/level/${levelIndex[1]}/`;
      return redirect(url);
    }

    const levelWithoutSlash = url.pathname.match(/^\/level\/([^/]+)$/);
    if (levelWithoutSlash) {
      url.pathname = `/level/${levelWithoutSlash[1]}/`;
      return redirect(url);
    }

    const assetPath = url.pathname.endsWith("/")
      ? `${url.pathname}index.html`
      : url.pathname;
    let response = await env.ASSETS.fetch(assetRequest(request, assetPath));

    if (response.status === 404 && url.pathname !== "/404.html") {
      const fallback = await env.ASSETS.fetch(assetRequest(request, "/404.html"));
      response = new Response(fallback.body, {
        status: 404,
        headers: fallback.headers,
      });
    }

    return withHeaders(response, url.hostname);
  },
};
