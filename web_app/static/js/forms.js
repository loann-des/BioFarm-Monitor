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

document.addEventListener("DOMContentLoaded", () => {
    const loadBtn = document.getElementById("load-stock");
    const resultDiv = document.getElementById("stock-result");

    loadBtn.addEventListener("click", async () => {
        resultDiv.innerHTML = "Chargement du stock...";

        try {
            const response = await fetch("/get_stock");
            const data = await response.json();

            if (data.success) {
                const {stock} = data;
                if (Object.keys(stock).length === 0) {
                    resultDiv.innerHTML = "Aucun stock disponible pour l'année en cours.";
                } else {
                    let html = "<table class='table table-bordered'><thead><tr><th>Médicament</th><th>Quantité</th></tr></thead><tbody>";
                    for (const [medic, qty] of Object.entries(stock)) {
                        html += `<tr><td>${medic}</td><td>${qty}</td></tr>`;
                    }
                    html += "</tbody></table>";
                    resultDiv.innerHTML = html;
                }
            } else {
                resultDiv.innerHTML = `Erreur : ${data.message}`;
            }
        } catch (error) {
            resultDiv.innerHTML = "Erreur lors du chargement.";
            console.error(error);
        }
    });
});


