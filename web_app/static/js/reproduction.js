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

        const contentType = response.headers.get("Content-Type");
        console.log("Have response of type: " + contentType);

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

  const dryButton = document.getElementById("load-dry");
  const calvingPrepButton = document.getElementById("load-calving_preparation");
  const calvingButton = document.getElementById("load-calving");

  dryButton.addEventListener("click", updateDryDates);
  calvingPrepButton.addEventListener("click", updateCalvingPreps);
  calvingButton.addEventListener("click", updateCalvingDates);
});

async function updateDryDates() {
  const dryResults = document.getElementById("dry-result");
  const response = await fetch("/show_dry");
  const data = JSON.parse(await response.text());

  console.log(data);

  if (data.success) {
    const { dry } = data;

    const sortedEntries = Object.entries(dry).sort((a, b) => {
        return new Date(a[1]) - new Date(b[1]);
    });

    if (Object.keys(dry).length !== 0) {
      if (!(dryResults.children[0] instanceof HTMLTableElement)) {
        console.log("No table");

        const tpl = document.querySelector("template#dry-table-template");
        const table = tpl.content.children[0].cloneNode(true);
        table.appendChild(document.createElement("tbody"));

        dryResults.appendChild(table);
      }

      const tbody = document.querySelector("div#dry-result table tbody");

      for (const [cowId, dateStr] of sortedEntries) {
        var found = false;

        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        for (const row of tbody.children) {
          if ((row.children[0].textContent == cowId.toString() || row.children[0].innerHTML == cowId.toString()) &&
              (row.children[1].textContent == formattedDate || row.children[1].innerHTML == formattedDate)) {
            found = true;
          }
        }

        if (!found) {
          const tpl = document.querySelector("template#dry-entry-template");
          const entry = tpl.content.children[0].cloneNode(true);

          const idColumn = entry.children[0];
          const dateColumn = entry.children[1];
          const validateButton = entry.children[2].children[0];

          idColumn.textContent = cowId.toString();
          idColumn.innerHTML = cowId.toString();

          dateColumn.textContent = formattedDate;
          dateColumn.innerHTML = formattedDate;

          validateButton.setAttribute("data-cow", cowId.toString());

          validateButton.addEventListener("click", async (e) => {
            const cowId = parseInt(e.target.getAttribute("data-cow"));

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
                e.target.closest("tr").remove();
              } else {
                alert(`Erreur lors de la validation`);
                console.error(result.message);
              }
            } catch (error) {
              console.error(error);
            }
          });

          tbody.appendChild(entry);
        }
      }
    }
  }
}

async function updateCalvingPreps() {
  const calvingPrepResults = document.getElementById("calving_preparation-result");
  const response = await fetch("/show_calving_preparation");
  const data = JSON.parse(await response.text());

  console.log(data);

  if (data.success) {
    console.log(`data is ${data}`);
    const calvingPreps = data["calving_preparation"];

    console.log(`calvingPreps is ${calvingPreps}`);

    const sortedEntries = Object.entries(calvingPreps).sort((a, b) => {
        return new Date(a[1]) - new Date(b[1]);
    });

    if (Object.keys(calvingPreps).length !== 0) {
      if (!(calvingPrepResults.children[0] instanceof HTMLTableElement)) {
        console.log("No table");

        const tpl = document.querySelector("template#calving-prep-table-template");
        const table = tpl.content.children[0].cloneNode(true);
        table.appendChild(document.createElement("tbody"));

        calvingPrepResults.appendChild(table);
      }

      const tbody = document.querySelector("div#calving_preparation-result table tbody");

      for (const [cowId, dateStr] of sortedEntries) {
        var found = false;

        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        for (const row of tbody.children) {
          if ((row.children[0].textContent == cowId.toString() || row.children[0].innerHTML == cowId.toString()) &&
              (row.children[1].textContent == formattedDate || row.children[1].innerHTML == formattedDate)) {
            found = true;
          }
        }

        if (!found) {
          const tpl = document.querySelector("template#calving-prep-entry-template");
          const entry = tpl.content.children[0].cloneNode(true);

          console.log(entry);

          const idColumn = entry.children[0];
          const dateColumn = entry.children[1];
          const validateButton = entry.children[2].children[0];

          idColumn.textContent = cowId.toString();
          idColumn.innerHTML = cowId.toString();

          dateColumn.textContent = formattedDate;
          dateColumn.innerHTML = formattedDate;

          validateButton.setAttribute("data-cow", cowId.toString());

          validateButton.addEventListener("click", async (e) => {
            const cowId = e.target.dataset.cow;
            try {
                const res = await fetch("/validate_calving_preparation", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ cow_id: cowId })
                });
                const result = await res.json();
                if (result.success) {
                    alert(`Préparation au vếlage validée pour la vache ${cowId}`);
                    e.target.closest("tr").remove(); // Supprime la ligne du tableau
                } else {
                    alert(`Erreur : ${result.message}`);
                }
            } catch (err) {
                console.error(err);
                alert("Erreur lors de la validation.");
            }
          });

          tbody.appendChild(entry);
        }
      }
    }
  }
}

async function updateCalvingDates() {
  const calvingResults = document.getElementById("calving-result");
  const response = await fetch("/show_calving_date");
  const data = JSON.parse(await response.text());

  console.log(data);

  if (data.success) {
    const calvings = data["calving"];

    const sortedEntries = Object.entries(calvings).sort((a, b) => {
        return new Date(a[1]) - new Date(b[1]);
    });

    if (Object.keys(calvings).length !== 0) {
      if (!(calvingResults.children[0] instanceof HTMLTableElement)) {
        console.log("No table");

        const tpl = document.querySelector("template#calving-table-template");
        const table = tpl.content.children[0].cloneNode(true);
        table.appendChild(document.createElement("tbody"));

        calvingResults.appendChild(table);
      }

      const tbody = document.querySelector("div#calving-result table tbody");

      for (const [cowId, dateStr] of sortedEntries) {
        var found = false;

        const formattedDate = new Date(dateStr).toLocaleDateString("fr-FR", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        for (const row of tbody.children) {
          if ((row.children[0].textContent == cowId.toString() || row.children[0].innerHTML == cowId.toString()) &&
              (row.children[1].textContent == formattedDate || row.children[1].innerHTML == formattedDate)) {
            found = true;
          }
        }

        if (!found) {
          const tpl = document.querySelector("template#calving-entry-template");
          const entry = tpl.content.children[0].cloneNode(true);

          entry.children[0].textContent = cowId.toString();
          entry.children[0].innerHTML = cowId.toString();

          entry.children[1].textContent = formattedDate;
          entry.children[1].innerHTML = formattedDate;

          tbody.appendChild(entry);
        }
      }
    }
  }
}
