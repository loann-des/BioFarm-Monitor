window.addEventListener("load", () => {
    loadMessages()

    const overlay = document.querySelector("div#overlay");

    // ------------------------------------------------------------------------------------------
    // Boutton PopUp echographie
    // ------------------------------------------------------------------------------------------
    const ultrasondButton = document.querySelector("button#ultrasound-button");
    const ultrasondPopup = document.querySelector("div.popup#add-ultrasound-popup");
    const ultrasondPopupCloseButton = document.querySelector("div.popup#add-ultrasound-popup div.popup-header button");

    ultrasondButton.addEventListener("click", async () => {
        overlay.style.display = "block";
        ultrasondPopup.style.display = "block";
    });

    ultrasondPopupCloseButton.addEventListener("click", async () => {
        overlay.style.display = "none";
        ultrasondPopup.style.display = "none";
        wipeField();
    });

    // ------------------------------------------------------------------------------------------
    // generation des option du select pour PopUp echographie
    // ------------------------------------------------------------------------------------------
    const echoInput = document.querySelector("#echo_cow_id");
    const echoSelect = document.querySelector("#echo_select");

    echoInput.addEventListener("change", async function () {

        const cowId = this.value;

        if (!cowId) return;

        try {
            const response = await fetch(`/reproduction/get-reproduction?id=${cowId}`);
            const data = await response.json();
            const { message } = data
            echoSelect.innerHTML = '<option value="" selected disabled>Choisir...</option>';

            if (!data.success) return;

            if (message != null)
                message["insemination"].forEach(
                    date => {
                        const dateObj = new Date(date);

                        date_formated = new Date(date).toLocaleDateString("fr-FR", {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        })

                        const today = new Date();
                        const diffMs = today - dateObj;
                        const diffWeeks = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 7));
                        const option = document.createElement("option");
                        option.value = date;
                        option.textContent = `${date_formated} (${diffWeeks} semaines)`;
                        echoSelect.appendChild(option);
                    }
                );
            let option = document.createElement("option");
            option.value = "saillie";
            option.textContent = `saillie`;
            echoSelect.appendChild(option);
            echoSelect.addEventListener("change", function () {
                let inputSaillie = document.getElementById("saillie");

                if (this.value === "saillie") {
                    inputSaillie.setAttribute("required", true);
                } else {
                    inputSaillie.removeAttribute("required");
                }
            });

            option = document.createElement("option");
            option.value = "Vide";
            option.textContent = `Vide`;

            echoSelect.appendChild(option);

        }
        catch (error) {
            console.error(error);
        }

    }
    );

    // ------------------------------------------------------------------------------------------
    // Boutton PopUp vêlage
    // ------------------------------------------------------------------------------------------
    const calvingButton = document.querySelector("button#calving-button");
    const calvingPopup = document.querySelector("div.popup#add-calving-popup");
    const calvingPopupCloseButton = document.querySelector("div.popup#add-calving-popup div.popup-header button");

    calvingButton.addEventListener("click", async () => {
        overlay.style.display = "block";
        calvingPopup.style.display = "block";
    });

    calvingPopupCloseButton.addEventListener("click", async () => {
        overlay.style.display = "none";
        calvingPopup.style.display = "none";
        wipeField();
    });

    const dryFilterInput = document.querySelector("div#id-filter-box-dry input");
    dryFilterInput.addEventListener("keyup", e => updateFiltered(e, updateDrying));

    const calvingPreparationFilterInput = document.querySelector("div#id-filter-box-calving-preparation input");
    calvingPreparationFilterInput.addEventListener("keyup", e => updateFiltered(e, updateCalvingPreparation));

    const calvingFilterInput = document.querySelector("div#id-filter-box-calving input");
    calvingFilterInput.addEventListener("keyup", e => updateFiltered(e, updateCalving));

    generalUpdate();
    const popupForms = document.querySelectorAll("form");
    for (const popupForm of popupForms) {
        message_form(popupForm);
    }
});

async function generalUpdate() {
    try {
        const response = await fetch(`/reproduction/get-all-reproductions`);
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
        updateCalving(reproductions)
        updateDrying(reproductions)
        updateCalvingPreparation(reproductions)
    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des velage.");
    }
}

async function updateCalving(reproductions) {
    const calvingList = document.querySelector("#calving-list");

    while (calvingList.children.length > 0) {
        calvingList.children[0].remove();
    }
    try {
        const calvingTemplate = document.querySelector("#calving-row");

        Object.entries(reproductions || {}).forEach(([cow_id, reproduction]) => {
            const Card = calvingTemplate.content.children[0].cloneNode(true);
            Card.querySelector(".cow_id").textContent = cow_id;

            calvingDate = new Date(reproduction["calving_date"]).toLocaleDateString("fr-FR", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            })

            Card.querySelector(".reproductions").textContent = calvingDate;

            calvingList.appendChild(Card);
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des calving.");
    }
}

async function updateDrying(reproductions) {
    const dryingList = document.querySelector("#dry-list");

    while (dryingList.children.length > 0) {
        dryingList.children[0].remove();
    }

    try {
        const calvingTemplate = document.querySelector("#other-row");

        Object.entries(reproductions || {}).forEach(([cow_id, reproduction]) => {
            if (!reproduction["dry_status"]) {
                const Card = calvingTemplate.content.children[0].cloneNode(true);
                const form = Card.querySelector("form")
                form.setAttribute("action", "/reproduction/drying")
                message_form(form)
                Card.querySelector("input").setAttribute("value", cow_id)
                Card.querySelector(".cow_id").textContent = cow_id;


                dryingDate = new Date(reproduction["dry"]).toLocaleDateString("fr-FR", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                })

                Card.querySelector(".reproductions").textContent = dryingDate;

                dryingList.appendChild(Card);
            }
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des calving.");
    }
}

async function updateCalvingPreparation(reproductions) {
    const calvingPreparationList = document.querySelector("#calving-preparation-list");
    while (calvingPreparationList.children.length > 0) {
        calvingPreparationList.children[0].remove();
    }
    try {
        const calvingPreparationTemplate = document.querySelector("#other-row");

        Object.entries(reproductions || {}).forEach(([cow_id, reproduction]) => {
            if (!reproduction["calving_preparation_status"]) {
                const Card = calvingPreparationTemplate.content.children[0].cloneNode(true);
                const form = Card.querySelector("form")
                form.setAttribute("action", "/reproduction/calving_preparation")
                message_form(form)

                Card.querySelector("input").setAttribute("value", cow_id)
                const cow = Card.querySelector(".cow_id").textContent = cow_id;

                calvingPreparationDate = new Date(reproduction["calving_preparation"]).toLocaleDateString("fr-FR", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                })

                Card.querySelector(".reproductions").textContent = calvingPreparationDate;

                calvingPreparationList.appendChild(Card);
            }
        });

    } catch (error) {
        console.error(`AJAX request failed due to: ${error}`);
        alert("Impossible de récupérer la liste des calving.");
    }
}

async function updateFiltered(e, updateFunction) {
    const filterInput = e.target;
    const filterId = parseInt(filterInput.value);

    const url = (filterId === undefined || isNaN(filterId))
        ? "/reproduction/get-all-reproductions"
        : "/reproduction/get-all-reproductions-filter?" +
        new URLSearchParams({ id_filter: filterId });

    const response = await fetch(url);

    const contentType = response.headers.get("Content-Type");

    if (!contentType.includes("application/json")) {
        console.error(`Filter failed: wrong response type (expected application/json, got ${contentType}`);
        console.log(response);
        return;
    }

    const result = await response.json();
    if (!result.success) {
        console.error(result.message);
        return;
    }

    const reproductions = result.message;
    updateFunction(reproductions);
}

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

async function wipeField() {
    const popupForms = document.querySelectorAll("div.popup form");

    for (const popupForm of popupForms) {

        popupForm.reset();
    }
}

async function message_form(elem) {
    // ------------------------------------------------------------------------------------------
    // gestion afficage message
    // ------------------------------------------------------------------------------------------
    elem.addEventListener("submit", async (e) => {
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

            elem.reset();

        } catch (error) {
            console.error(`AJAX request failed due to ${error}`);
        }

        location.reload()
    });
}