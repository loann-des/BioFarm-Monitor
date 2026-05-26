let timeoutId;
window.addEventListener("load", () => {
    loadMessages();

    const prescriptionButton = document.querySelector("button#add-prescription-button");
    const dlcLeftButton = document.querySelector("button#add-dcl-left-button");
    const recapCowsButton = document.querySelector("button#export-recap-cows-button");
    const recapPharmacyButton = document.querySelector("button#export-recap-pharmacy-button");
    const overlay = document.querySelector("div#overlay");



    const prescriptionPopup = document.querySelector("div.popup#add-prescription-popup");
    const prescriptionPopupCloseButton = document.querySelector("div.popup#add-prescription-popup div.popup-header button");

    prescriptionButton.addEventListener("click", async () => {
        overlay.style.display = "block";
        prescriptionPopup.style.display = "block";
    });

    prescriptionPopupCloseButton.addEventListener("click", async () => {
        overlay.style.display = "none";
        prescriptionPopup.style.display = "none";
    });

    const prescriptionMedicationTemplate = document.querySelector("#medication-template");
    const prescriptionContainer = document.querySelector("#medication-extend-treatment");

    const addMedicationButtonTreatment = document.querySelector("div#btn-ext-treatment button#extend-medication");
    addMedicationButtonTreatment.addEventListener("click", () => {
        const card = prescriptionMedicationTemplate.content.children[0].cloneNode(true);
        prescriptionContainer.appendChild(card);
    });

    const removeMedicationButtonTreatment = document.querySelector("div#btn-ext-treatment button#remove-medication");
    removeMedicationButtonTreatment.addEventListener("click", () => {
        if (prescriptionContainer.children.length > 1) {
            prescriptionContainer.removeChild(prescriptionContainer.lastElementChild);
        }
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

    const dlcLeftPopup = document.querySelector("div.popup#add-dcl-left-popup");
    const dlcLeftClose = document.querySelector("div.popup#add-dcl-left-popup div.popup-header button");

    dlcLeftButton.addEventListener("click", () => {
        overlay.style.display = "block";
        dlcLeftPopup.style.display = "block";
    });

    dlcLeftClose.addEventListener("click", () => {
        overlay.style.display = "none";
        dlcLeftPopup.style.display = "none";
    });

    const dlcMedicationTemplate = document.querySelector("#medication-template");
    const dlcContainer = document.querySelector("#medication-extend-dlc");

    const addMedicationButtonDlc = document.querySelector("div#btn-ext-dlc button#extend-medication");
    addMedicationButtonDlc.addEventListener("click", () => {
        const card = dlcMedicationTemplate.content.children[0].cloneNode(true);
        dlcContainer.appendChild(card);
    });

    const removeMedicationButtonDlc = document.querySelector("div#btn-ext-dlc button#remove-medication");
    removeMedicationButtonDlc.addEventListener("click", () => {
        if (dlcContainer.children.length > 1) {
            dlcContainer.removeChild(dlcContainer.lastElementChild);
        }
    });

    updateStock();
    updatePrescription();
    updateDlc();

});

async function loadMessages() {

    const msg =
        sessionStorage.getItem(
            "flashMessage"
        );

    if (msg) {

        const result =
            JSON.parse(msg);

        const errorprescriptionContainer =
            document.querySelector(
                "#message-div"
            );

        const errorTextprescriptionContainer =
            document.querySelector(
                "#message-div span"
            );

        errorprescriptionContainer.classList.remove(
            "message-div",
            "error-div",
            "success-div"
        );

        errorprescriptionContainer.classList.add(
            result.success
                ? "success-div"
                : "error-div"
        );

        errorTextprescriptionContainer.textContent =
            result.message;

        setTimeout(() => {

            errorprescriptionContainer.classList.remove(
                "error-div",
                "success-div"
            );

            errorprescriptionContainer.classList.add(
                "message-div"
            );

        }, 5000);

        sessionStorage.removeItem(
            "flashMessage"
        );
    }

}

async function updateStock() {
    const stockList = document.querySelector("#stock-list");

    try {
        const response = await fetch(`/pharmacy/get-stock`);

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

        const medication = result.message;

        const StockTemplate = document.querySelector(
            "#stock-row"
        );

        Object.entries(medication || {}).forEach(([medication, dose]) => {
            const Card = StockTemplate.content.children[0].cloneNode(true);
            Card.querySelector(".medication").textContent = medication;

            Card.querySelector(".dose").textContent = dose;
            stockList.appendChild(Card);
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des stock.");
    }
}


async function updatePrescription() {
    const prescriptionList = document.querySelector("#prescription-list");

    try {
        const response = await fetch(`/pharmacy/get-prescription`);

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

        const prescriptions = result.message;

        let index = 0;


        prescriptions.forEach(prescription => {

            const prescriptionTemplate = document.querySelector(
                "#prescription-dlc-template"
            );

            const card = prescriptionTemplate.content.children[0].cloneNode(true);

            const date = new Date(prescription["date_prescription"]).toLocaleDateString("fr-FR", {
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

            Object.entries(prescription["prescription"] || {})
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

            card.querySelector(".title").textContent = `prescription du ${date}`;
            // TODO Change btn
            // card.querySelector("button#prescription-change-button").setAttribute("prescription_id", prescription["id"]);
            card.querySelector("button#prescription-delete-button").setAttribute("prescription_id", prescription["id"]);

            card.querySelector("button#prescription-delete-button").addEventListener("click", async (e) => {
                if (!confirm('Are you sure?')) {
                    return;
                }

                const prescription_id = e.currentTarget.getAttribute("prescription_id");

                let reqData = new FormData();
                reqData.append("prescription_id", prescription_id);

                const response = await fetch("/pharmacy/remove-prescription", {
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

            // card.querySelector("button#prescription-change-button").addEventListener("click", async (e) => {
            //     const changeprescriptionPopup = document.querySelector("div.popup#change-prescription-popup");
            //     changeprescriptionPopup.querySelector(".popup-title").textContent = `Modifier les soins du ${date}`;
            //     changeprescriptionPopup.querySelector(".date").value =
            //         new Date(prescription["date_traitement"]).toISOString().split("T")[0];
            //     changeprescriptionPopup.querySelector(".annotation").value = prescription["annotation"] || "";

            //     const medicationContainer = changeprescriptionPopup.querySelector("#medication-extend");
            //     while (medicationContainer.children.length > 0) {
            //         medicationContainer.removeChild(medicationContainer.lastElementChild);
            //     }
            //     const medicationTemplate = document.querySelector("#medication-template");
            //     Object.entries(prescription["medicaments"] || {}).forEach(([medication, dose]) => {
            //         const medCard = medicationTemplate.content.children[0].cloneNode(true);
            //         medCard.querySelector(".medication").value = medication;

            //         medCard.querySelector(".dose").value = dose;
            //         medicationContainer.appendChild(medCard);
            //     });

            //     changeprescriptionPopup.querySelector(".index").setAttribute("value", index);

            //     changeprescriptionPopup.style.display = "block";
            // });

            prescriptionList.appendChild(card);
            index++;
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des soins.");
    }
}

async function updateDlc() {
    const dlcList = document.querySelector("#dlc-list");

    try {
        const response = await fetch(`/pharmacy/get-dlc-left`);

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

        const dlcs = result.message;

        dlcs.forEach(dlc => {

            const dlcTemplate = document.querySelector(
                "#prescription-dlc-template"
            );

            const card = dlcTemplate.content.children[0].cloneNode(true);

            const date = new Date(dlc["date_prescription"]).toLocaleDateString("fr-FR", {
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

            Object.entries(dlc["prescription"] || {})
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

            card.querySelector(".title").textContent = `sortie pour dlc du ${date}`;
            // TODO Change btn
            // card.querySelector("button#prescription-change-button").setAttribute("prescription_id", dlc["id"]);
            card.querySelector("button#prescription-delete-button").setAttribute("prescription_id", dlc["id"]);

            card.querySelector("button#prescription-delete-button").addEventListener("click", async (e) => {
                if (!confirm('Are you sure?')) {
                    return;
                }

                const prescription_id = e.currentTarget.getAttribute("prescription_id");

                let reqData = new FormData();
                reqData.append("index", index);

                const response = await fetch("/cow/remove_prescription", {
                    method: "POST",
                    body: reqData
                });
                // TODO

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

            // card.querySelector("button#prescription-change-button").addEventListener("click", async (e) => {
            //     const changeprescriptionPopup = document.querySelector("div.popup#change-prescription-popup");
            //     changeprescriptionPopup.querySelector(".popup-title").textContent = `Modifier les soins du ${date}`;
            //     changeprescriptionPopup.querySelector(".date").value =
            //         new Date(prescription["date_traitement"]).toISOString().split("T")[0];
            //     changeprescriptionPopup.querySelector(".annotation").value = prescription["annotation"] || "";

            //     const medicationContainer = changeprescriptionPopup.querySelector("#medication-extend");
            //     while (medicationContainer.children.length > 0) {
            //         medicationContainer.removeChild(medicationContainer.lastElementChild);
            //     }
            //     const medicationTemplate = document.querySelector("#medication-template");
            //     Object.entries(prescription["medicaments"] || {}).forEach(([medication, dose]) => {
            //         const medCard = medicationTemplate.content.children[0].cloneNode(true);
            //         medCard.querySelector(".medication").value = medication;

            //         medCard.querySelector(".dose").value = dose;
            //         medicationContainer.appendChild(medCard);
            //     });

            //     changeprescriptionPopup.querySelector(".index").setAttribute("value", index);

            //     changeprescriptionPopup.style.display = "block";
            // });
            // TODO Change btn
            dlcList.appendChild(card);
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des sortie pour dlc.");
    }
}