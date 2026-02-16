window.addEventListener("load", () => {
  const loginForm = document.querySelector("form");
  const errorContainer = document.querySelector("div#error-div");
  const errorTextContainer = document.querySelector("div#error-div span");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const action = e.target.getAttribute("action");
    const method = e.target.getAttribute("method");
    const data = new FormData(e.target);

    try {
      const response = await fetch(action, {
        method: method,
        body: data
      });

      const contentType = response.headers.get("Content-Type");

      if (contentType.includes("application/json")) {
        const result = await response.json();

        if (result.success) {
          console.log("Authentication succeeded but redirection failed");

          errorTextContainer.textContent = "Authentification réussie, mais échec de redirection";
          errorTextContainer.innerHTML = "Authentification réussie, mais échec de redirection";
          errorContainer.style.display = "block";
        } else {
          console.log(`Authentication failed: ${result.message}`);

          errorTextContainer.textContent = result.message;
          errorTextContainer.innerHTML = result.message;
          errorContainer.style.display = "block";
        }
      } else {
        window.location = "/";
      }
    } catch (error) {
      console.log(`AJAX request failed due to ${error}`);

      errorTextContainer.textContent = "Connexion impossible";
      errorTextContainer.innerHTML = "Connexion impossible";
      errorContainer.style.display = "block";
    }
  });
});
