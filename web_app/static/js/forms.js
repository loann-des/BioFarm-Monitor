console.log("forms.js chargé");

// Js message/alert
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

// Js get_stock
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

//Js show_dry
document.addEventListener("DOMContentLoaded", () => {
    const loadBtn = document.getElementById("load-dry");
    const resultDiv = document.getElementById("dry-result");

    loadBtn.addEventListener("click", async () => {
        resultDiv.innerHTML = "Chargement ...";

        try {
            const response = await fetch("/show_dry");
            const data = await response.json();

            if (data.success) {
                const { dry } = data;
                if (Object.keys(dry).length === 0) {
                    resultDiv.innerHTML = "Aucun tarissement à prévoir.";
                } else {
                    let html = "<table class='table table-bordered'><thead><tr><th>Vache</th><th>Tarissement</th><th>Action</th></tr></thead><tbody>";

                    const sortedEntries = Object.entries(dry).sort((a, b) => {
                        return new Date(a[1]) - new Date(b[1]);
                    });

                    for (const [cowId, dateStr] of sortedEntries) {
                        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        });
                        html += `
                            <tr>
                                <td>${cowId}</td>
                                <td>${formattedDate}</td>
                                <td><button class="btn btn-success validate-btn" data-cow="${cowId}">Valider</button></td>
                            </tr>
                        `;
                    }

                    html += "</tbody></table>";
                    resultDiv.innerHTML = html;

                    // Ajouter les écouteurs pour les boutons valider
                    document.querySelectorAll(".validate-btn").forEach(btn => {
                        btn.addEventListener("click", async (e) => {
                            const cowId = e.target.dataset.cow;
                            try {
                                const res = await fetch("/validate_dry", {
                                    method: "POST",
                                    headers: {
                                        "Content-Type": "application/json"
                                    },
                                    body: JSON.stringify({ cow_id: cowId })
                                });
                                const result = await res.json();
                                if (result.success) {
                                    alert(`Tarissement validé pour la vache ${cowId}`);
                                    e.target.closest("tr").remove(); // Supprime la ligne du tableau
                                } else {
                                    alert(`Erreur : ${result.message}`);
                                }
                            } catch (err) {
                                console.error(err);
                                alert("Erreur lors de la validation.");
                            }
                        });
                    });
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


//Js show_calving_preparation
document.addEventListener("DOMContentLoaded", () => {
    const loadBtn = document.getElementById("load-calving_preparation");
    const resultDiv = document.getElementById("calving_preparation-result");

    loadBtn.addEventListener("click", async () => {
        resultDiv.innerHTML = "Chargement ...";

        try {
            const response = await fetch("/show_calving_preparation");
            const data = await response.json();

            if (data.success) {
                const {calving_preparation} = data;
                if (Object.keys(calving_preparation).length === 0) {
                    resultDiv.innerHTML = "Aucun prepa velage à prévoir.";
                } else {
                    let html = "<table class='table table-bordered'><thead><tr><th>Vache</th><th>Tarrissement</th></tr></thead><tbody>";

                    const sortedEntries = Object.entries(calving_preparation).sort((a, b) => {
                        return new Date(a[1]) - new Date(b[1]);
                    });

                    for (const [cowId, dateStr] of sortedEntries) {
                        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        });
                        html += `<tr><td>${cowId}</td><td>${formattedDate}</td></tr>`;
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

//Js show_calving_date
document.addEventListener("DOMContentLoaded", () => {
    const loadBtn = document.getElementById("load-calving");
    const resultDiv = document.getElementById("calving-result");

    loadBtn.addEventListener("click", async () => {
        resultDiv.innerHTML = "Chargement ...";

        try {
            const response = await fetch("/show_calving_date");
            const data = await response.json();

            if (data.success) {
                const {calving} = data;
                if (Object.keys(calving).length === 0) {
                    resultDiv.innerHTML = "Aucun prepa velage à prévoir.";
                } else {
                    let html = "<table class='table table-bordered'><thead><tr><th>Vache</th><th>Tarrissement</th></tr></thead><tbody>";

                    const sortedEntries = Object.entries(calving).sort((a, b) => {
                        return new Date(a[1]) - new Date(b[1]);
                    });

                    for (const [cowId, dateStr] of sortedEntries) {
                        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        });
                        html += `<tr><td>${cowId}</td><td>${formattedDate}</td></tr>`;
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

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formId = this.id;
      const messageBox = document.getElementById(`message-${formId}`);
      if (!messageBox) return;

      // reset
      messageBox.className = "alert";
      messageBox.style.display = "none";

      try {
        const response = await fetch(this.action, {
          method: this.method || "POST",
          body: new FormData(this),
        });

        const contentType = response.headers.get("Content-Type") || "";

        if (contentType.includes("application/json")) {
          // Réponse JSON → affiche status
          const result = await response.json();
          if (result.success) {
            messageBox.classList.add("alert-success");
            messageBox.textContent = result.message || "Succès.";
          } else {
            messageBox.classList.add("alert-danger");
            messageBox.textContent = result.message || "Erreur.";
          }
          messageBox.style.display = "block";
        } else {
          // Réponse fichier → téléchargement
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

          // message succès
          messageBox.classList.add("alert-success");
          messageBox.textContent = "Téléchargement réussi.";
          messageBox.style.display = "block";
        }
      } catch (error) {
        messageBox.classList.add("alert-danger");
        messageBox.textContent = "Erreur réseau.";
        messageBox.style.display = "block";
        console.error(error);
      }
    });
  });
});



