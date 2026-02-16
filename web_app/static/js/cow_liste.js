window.addEventListener("load", () => {
  const forms = document.querySelectorAll("form.ajax-form");

  forms.forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formId = e.target.getAttribute("id");
      const messageBox = document.getElementById(`message-${formId}`);

      const action = e.target.getAttribute("action");
      const method = e.target.getAttribute("method");
      const formData = new FormData(e.target);

      try {
        const response = await fetch(action, {
          method: method,
          body: formData
        });

        const contentType = response.headers.get("Content-Type");

        if (contentType.includes("application/json")) {
          const data = JSON.parse(await response.text());

          console.log(data);

          if (data.success) {
            e.target.parentNode.remove();
          } else {
            messageBox.textContent = data.message;
            messageBox.innerHTML = data.message;
            messageBox.style.display = "block";
          }
        } else {
          messageBox.textContent = "Error: response is not a valid JSON";
          messageBox.innerHTML = "Error: response is not a valid JSON";
          messageBox.style.display = "block";
        }
      } catch (error) {
        messageBox.textContent = error;
        messageBox.innerHTML = error;
        messageBox.style.display = "block";
      }
    });
  });
});
