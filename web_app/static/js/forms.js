console.log("forms.js chargé");

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form.ajax-form").forEach(function (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault(); // ← C'est ce qui empêche le rechargement / affichage JSON brut

      const formData = new FormData(form);
      const action = form.getAttribute("action");

      try {
        const response = await fetch(action, {
          method: "POST",
          body: formData,
        });

        const result = await response.json();

        // Affiche le message dans la section liée
        const formId = form.getAttribute("id");
        const messageElement = document.getElementById("message-" + formId);
        messageElement.classList.remove("alert-success", "alert-danger");
        messageElement.style.display = "block";

        if (result.success) {
          messageElement.classList.add("alert-success");
          messageElement.textContent = result.message || "Succès";
        } else {
          messageElement.classList.add("alert-danger");
          messageElement.textContent = result.message || "Erreur";
        }
      } catch (error) {
        console.error("Erreur AJAX :", error);
      }
    });
  });
});
