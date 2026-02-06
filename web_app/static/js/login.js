//JavaScript document
window.addEventListener("load", () => {
  const form = document.querySelector("form");
  const errorDiv = document.querySelector("form div#error-div");
  const errorText = document.querySelector("form div#error-div span");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const action = e.target.getAttribute("action");
    const formData = new FormData(e.target);

    try {
      const response = await fetch(action, {
        method: "POST",
        body: formData
      });

      const contentType = response.headers.get("Content-Type") || "";
      console.log("Have response type " + contentType);

      if (contentType.includes("application/json")) {
        const result = JSON.parse(await response.text());

        if (result.success) {
          console.log("Success");
        } else {
          errorText.textContent = result.message;
          // innerHTML retains compatibility with legacy browsers.
          // To be used with care as its content is added to the target as HTML.
          errorText.innerHTML = result.message;

          errorDiv.style.display = "block";
        }
      } else {
        window.location = "/";
      }
    } catch (error) {
      console.error("Failed to complete AJAX transaction: " + error);
    }
  });
});
