window.addEventListener("load", () => {
  const forms = document.querySelectorAll("form.ajax-form");

  forms.forEach((element) => {
    document.addEventListener("submit", async (e) => {
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

        const contentType = response.headers.get("Content-Type") || "";
        console.log("Have response of type" + contentType);

        if (contentType.includes("application/json")) {
          const result = JSON.parse(await response.text());

          if (result.success) {
            messageBox.classList.add("success");
          } else {
            messageBox.classList.add("alert");
          }

          messageBox.textContent = result.message;
          messageBox.innerHTML = result.message;
          messageBox.style.display = "block";
        } else {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download =
            response.headers.get("Content-Disposition")?.split("filename=")[1]?.replace(/"/g, "") ||
            "export";
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        }
      } catch (error) {
        messageBox.textContent = error;
        messageBox.innerHTML = error;
        messageBox.style.display = "block";
      }
    });
  });
});
