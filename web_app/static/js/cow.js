let cowId;
let timeoutId;
window.addEventListener("load", () => {
  loadMessages();

  const changeButton = document.querySelector("button#change-button");
  const inseminationButton = document.querySelector("button#insemination-button");
  const treatmentButton = document.querySelector("button#treatment-button");
  const removeButton = document.querySelector("button#delete-button");
  const overlay = document.querySelector("div#overlay");

  cowId = parseInt(removeButton.getAttribute("cow"));



  const changePopup = document.querySelector("div.popup#change-cow-div");
  const changePopupCloseButton = document.querySelector("div.popup#change-cow-div div.popup-header button");

  changeButton.addEventListener("click", async () => {
    overlay.style.display = "block";
    changePopup.style.display = "block";
  });

  changePopupCloseButton.addEventListener("click", async () => {
    overlay.style.display = "none";
    changePopup.style.display = "none";
  });

  const popupForms = document.querySelectorAll("div.popup form");

  for (const popupForm of popupForms) {
    popupForm.addEventListener("submit", async (e) => {
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

        if (!contentType.includes("application/json")) {
          console.error(`Unexpected response: expected application/json, got ${contentType}`);
          // TODO: Proper error display on the user's side
          return;
        }

        const result = await response.json();
        sessionStorage.setItem(
          "flashMessage",
          JSON.stringify(result)
        );

      } catch (error) {
        console.error(`AJAX request failed due to ${error}`);
      }

      location.reload()
    });
  }

  const inseminationPopup = document.querySelector("div.popup#insemination-popup");
  const inseminationClose = document.querySelector("div.popup#insemination-popup div.popup-header button");

  inseminationButton.addEventListener("click", () => {
    overlay.style.display = "block";
    inseminationPopup.style.display = "block";
  });

  inseminationClose.addEventListener("click", () => {
    overlay.style.display = "none";
    inseminationPopup.style.display = "none";
  });

  const treatmentPopup = document.querySelector("div.popup#treatment-popup");
  const treatmentClose = document.querySelector("div.popup#treatment-popup div.popup-header button");

  treatmentButton.addEventListener("click", () => {
    overlay.style.display = "block";
    treatmentPopup.style.display = "block";
  });

  treatmentClose.addEventListener("click", () => {
    overlay.style.display = "none";
    treatmentPopup.style.display = "none";
  });


  const addMedicationButton = document.querySelector("div#btn-ext-treatment button#extend-medication");
  const removeMedicationButton = document.querySelector("div#btn-ext-treatment button#remove-medication");

  const medicationTemplate = document.querySelector("#medication-template");
  const container = document.querySelector("#medication-extend");
  addMedicationButton.addEventListener("click", () => {
    const card = medicationTemplate.content.children[0].cloneNode(true);
    container.appendChild(card);
  });

  removeMedicationButton.addEventListener("click", () => {
    if (container.children.length > 1) {
      container.removeChild(container.lastElementChild);
    }
  });

  const addChangeMedicationButton = document.querySelector("div#btn-ext-change-care button#extend-medication");
  const removeChangeMedicationButton = document.querySelector("div#btn-ext-change-care button#remove-medication");

  const medicationChangeTemplate = document.querySelector("div#change-care-popup #medication-template");
  const changeContainer = document.querySelector("div#change-care-popup #medication-extend");

  addChangeMedicationButton.addEventListener("click", () => {
    const card = medicationChangeTemplate.content.children[0].cloneNode(true);
    changeContainer.appendChild(card);
  });

  removeChangeMedicationButton.addEventListener("click", () => {
    if (changeContainer.children.length > 1) {
      changeContainer.removeChild(changeContainer.lastElementChild);
    }
  });


  removeButton.addEventListener("click", async () => {
    if (!confirm('Are you sure?')) {
      return;
    }
    let reqData = new FormData();
    reqData.append("id", cowId);

    const response = await fetch("/cow/remove", {
      method: "POST",
      body: reqData
    });

    const contentType = response.headers.get("Content-Type");

    if (!contentType.includes("application/json")) {
      console.error(`Unexpected response: expected application/json, got ${contentType}`);
      return;
    }

    const json = await response.json();

    if (json.success == true) {
      console.log("Success");
      window.location = "/herd"
    } else {
      console.log("Failed");
    }
  });

  const changeReproductionClose = document.querySelector("div.popup#change-reproduction-popup div.popup-header button");

  changeReproductionClose.addEventListener("click", () => {
    overlay.style.display = "none";
    document.querySelector("div.popup#change-reproduction-popup").style.display = "none";
  });

  const changeCareClose = document.querySelector("div.popup#change-care-popup div.popup-header button");

  changeReproductionClose.addEventListener("click", () => {
    overlay.style.display = "none";
    document.querySelector("div.popup#change-reproduction-popup").style.display = "none";
  });

  changeCareClose.addEventListener("click", () => {
    overlay.style.display = "none";
    document.querySelector("div.popup#change-care-popup").style.display = "none";
  });



  updateCow();
});

async function updateCowReproductions() {
  const reproductionList = document.querySelector("#reproduction-list");
  const changeReproductionPopup = document.querySelector("div.popup#change-reproduction-popup");


  try {
    const response = await fetch(`/cow/get-reproductions?cow_id=${cowId}`);

    const contentType = response.headers.get("Content-Type");
    if (!(contentType.includes("application/json"))) {
      console.error(`list: AJAX request failed: expected application/json response, got ${contentType}`);
      console.log(await response.text());
      return;
    }

    const result = await response.json();
    if (!result.success) {
      console.error(result.message);
      return;
    }

    const reproductions = result.message;

    let index = 0;
    reproductions.forEach(reproduction => {

      console.log(reproduction["insemination"]);

      const date = reproduction["insemination"]
        .map(insemination =>
          new Date(insemination).toLocaleDateString(
            "fr-FR",
            {
              day: "2-digit",
              month: "short",
              year: "numeric"
            }
          )
        )
        .join(", ");

      const template = document.querySelector(
        "#reproduction-template"
      );

      const card = template.content.children[0].cloneNode(true);

      card.querySelector(".title").textContent = `Insémination du ${date}`;

      card.querySelector(".status").textContent =
        reproduction["calving"] ? "Terminée" : "En cours";

      card.querySelector(".echo").textContent =
        reproduction["ultrasound"] === null ? "En attente" :
          reproduction["ultrasound"] ? "Pleine" : "Vide";

      card.querySelector(".dry").textContent = reproduction["dry"] ? new Date(reproduction["dry"]).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      }) : "En attente";

      card.querySelector(".prep").textContent = reproduction["calving_preparation"] ? new Date(reproduction["calving_preparation"]).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      }) : "En attente";

      card.querySelector(".calving").textContent = reproduction["calving_date"] ? new Date(reproduction["calving_date"]).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      }) : "En attente";

      card.querySelector(".abortion").textContent =
        reproduction["abortion"] === null ? "En attente" :
          reproduction["abortion"] ? "avortement" : "non";

      card.querySelector(".details-content").textContent =
        reproduction["reproduction_details"] || "Aucune information supplémentaire";

      card.querySelector("button#reproduction-change-button").setAttribute("index", index);
      card.querySelector("button#reproduction-delete-button").setAttribute("index", index);

      reproductionList.appendChild(card);

      card.querySelector("button#reproduction-delete-button").addEventListener("click", async (e) => {
        if (!confirm('Are you sure?')) {
          return;
        }

        const index = e.currentTarget.getAttribute("index");

        let reqData = new FormData();
        reqData.append("cow_id", cowId);
        reqData.append("index", index);

        const response = await fetch("/cow/remove_reproduction", {
          method: "POST",
          body: reqData
        });

        const contentType = response.headers.get("Content-Type");

        if (!contentType.includes("application/json")) {
          console.error(`Unexpected response: expected application/json, got ${contentType}`);
          return;
        }

        const result = await response.json();
        sessionStorage.setItem(
          "flashMessage",
          JSON.stringify(result)
        );

        location.reload()
      });

      card.querySelector("button#reproduction-change-button").addEventListener("click", async (e) => {
        changeReproductionPopup.querySelector(".popup-title").textContent = `Modifier la reproduction du ${date}`;
        changeReproductionPopup.querySelector(".index").setAttribute("value", index);
        // changeReproductionPopup.querySelector(".insemination").setAttribute("value", reproduction["insemination"] ? new Date(reproduction["insemination"]).toISOString().split("T")[0] : "");

        changeReproductionPopup.querySelector(".echo").value =
          reproduction["ultrasound"] === null ? "None" :
            reproduction["ultrasound"] ? "1" : "";

        changeReproductionPopup.querySelector(".dry").value =
          reproduction["dry_status"] ? "1" : "";

        changeReproductionPopup.querySelector(".prep").value =
          reproduction["calving_preparation_status"] ? "1" : "";

        changeReproductionPopup.querySelector(".calving").value =
          reproduction["calving"] ? "1" : "";

        changeReproductionPopup.querySelector(".abortion").value =
          reproduction["abortion"] ? "1" : "";

        changeReproductionPopup.querySelector(".details-content").value =
          reproduction["reproduction_details"] || "";

        changeReproductionPopup.querySelector(".index").setAttribute("value", index);

        const inseminationDateContainer = changeReproductionPopup.querySelector("#insemination-container");
        while (inseminationDateContainer.children.length > 0) {
          inseminationDateContainer.removeChild(inseminationDateContainer.lastElementChild);
        }
        const inseminationDateTemplate = document.querySelector("#insemination-date-template");

        let count = 0;
        reproduction["insemination"].forEach(insemination => {
          cardInsemination = inseminationDateTemplate.content.cloneNode(true);
          cardInsemination.querySelector("label").textContent = `Insemination ${count + 1}`;
          cardInsemination.querySelector("input").setAttribute("value", new Date(insemination).toISOString().split("T")[0]);
          inseminationDateContainer.appendChild(cardInsemination);
          count++;
        });


        changeReproductionPopup.style.display = "block";
        index++;
      });
    });


  } catch (error) {
    console.error(`AJAX request failed due to: ${error}`);
    alert("Impossible de récupérer la liste des reproductions.");
  }
}

async function updateCowCares() {
  const careList = document.querySelector("#care-list");

  try {
    const response = await fetch(`/cow/get-cares?cow_id=${cowId}`);

    const contentType = response.headers.get("Content-Type");
    if (!(contentType.includes("application/json"))) {
      console.error(`list: AJAX request failed: expected application/json response, got ${contentType}`);
      console.log(await response.text());
      return;
    }

    const result = await response.json();
    if (!result.success) {
      console.error(result.message);
      return;
    }

    const cares = result.message;

    let index = 0;

    cares.forEach(care => {

      const careTemplate = document.querySelector(
        "#care-template"
      );

      const card = careTemplate.content.children[0].cloneNode(true);

      const date = new Date(care["date_traitement"]).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      })

      const medicationList =
        card.querySelector(
          ".medication-list"
        );

      const medicationTemplate =
        card.querySelector(".medication-template");

      Object.entries(care["medicaments"] || {})
        .forEach(([medication, dose]) => {

          const medCard =
            medicationTemplate.content.children[0].cloneNode(true);

          medCard.querySelector(".medication").textContent =
            medication + ":";

          medCard.querySelector(".dose").textContent =
            dose;

          medicationList.appendChild(medCard);

        });
      medicationTemplate.remove();

      const details = care["annotation"] || "Aucune information supplémentaire";
      card.querySelector(".title").textContent = `Soins du ${date}`;
      card.querySelector(".details-content").textContent = details;

      card.querySelector("button#care-change-button").setAttribute("index", index);
      card.querySelector("button#care-delete-button").setAttribute("index", index);

      card.querySelector("button#care-delete-button").addEventListener("click", async (e) => {
        if (!confirm('Are you sure?')) {
          return;
        }

        const index = e.currentTarget.getAttribute("index");

        let reqData = new FormData();
        reqData.append("cow_id", cowId);
        reqData.append("index", index);

        const response = await fetch("/cow/remove_care", {
          method: "POST",
          body: reqData
        });

        const contentType = response.headers.get("Content-Type");

        if (!contentType.includes("application/json")) {
          console.error(`Unexpected response: expected application/json, got ${contentType}`);
          return;
        }

        const result = await response.json();
        sessionStorage.setItem(
          "flashMessage",
          JSON.stringify(result)
        );

        location.reload()
      });

      card.querySelector("button#care-change-button").addEventListener("click", async (e) => {
        const changeCarePopup = document.querySelector("div.popup#change-care-popup");
        changeCarePopup.querySelector(".popup-title").textContent = `Modifier les soins du ${date}`;
        changeCarePopup.querySelector(".date").value =
          new Date(care["date_traitement"]).toISOString().split("T")[0];
        changeCarePopup.querySelector(".annotation").value = care["annotation"] || "";

        const medicationContainer = changeCarePopup.querySelector("#medication-extend");
        while (medicationContainer.children.length > 0) {
          medicationContainer.removeChild(medicationContainer.lastElementChild);
        }
        const medicationTemplate = document.querySelector("#medication-template");
        Object.entries(care["medicaments"] || {}).forEach(([medication, dose]) => {
          const medCard = medicationTemplate.content.children[0].cloneNode(true);
          medCard.querySelector(".medication").value = medication;

          medCard.querySelector(".dose").value = dose;
          medicationContainer.appendChild(medCard);
        });

        changeCarePopup.querySelector(".index").setAttribute("value", index);

        changeCarePopup.style.display = "block";
      });

      careList.appendChild(card);
      index++;
    });

  } catch (error) {
    console.error(`AJAX request failed due to: ${error}`);
    alert("Impossible de récupérer la liste des soins.");
  }
}

async function loadMessages() {

  const msg =
    sessionStorage.getItem(
      "flashMessage"
    );

  if (msg) {

    const result =
      JSON.parse(msg);

    const errorContainer =
      document.querySelector(
        "#message-div"
      );

    const errorTextContainer =
      document.querySelector(
        "#message-div span"
      );

    errorContainer.classList.remove(
      "message-div",
      "error-div",
      "success-div"
    );

    errorContainer.classList.add(
      result.success
        ? "success-div"
        : "error-div"
    );

    errorTextContainer.textContent =
      result.message;

    setTimeout(() => {

      errorContainer.classList.remove(
        "error-div",
        "success-div"
      );

      errorContainer.classList.add(
        "message-div"
      );

    }, 5000);

    sessionStorage.removeItem(
      "flashMessage"
    );
  }

}

async function updateCow() {
  await updateCowReproductions();
  await updateCowCares();
}