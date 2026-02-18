window.addEventListener("load", async () => {
  const addCowButton = document.querySelector("button#add-cow-button");
  const overlay = document.querySelector("div#overlay");
  const popup = document.querySelector("div.popup");
  const popupCloseButton = document.querySelector("div.popup div.popup-header button");

  addCowButton.addEventListener("click", () => {
    overlay.style.display = "block";
    popup.style.display = "flex";
  });

  popupCloseButton.addEventListener("click", () => {
    overlay.style.display = "none";
    popup.style.display = "none";
  });

  const popupForm = document.querySelector("div.popup form");

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

      console.log(response);

      updateHerd();
    } catch (error) {
      console.error(`AJAX request failed due to ${error}`);
      // TODO: Proper error display on the user's side
    }

    overlay.style.display = "none";
    popup.style.display = "none";
  });

  updateHerd();
});

async function updateHerd() {
  const herdTable = document.querySelector("table tbody");

  while (herdTable.children.length > 0) {
    herdTable.children[0].remove();
  }

  try {
    const response = await fetch("/cow_liste/list_cows");

    const contentType = response.headers.get("Content-Type");

    if (!(contentType.includes("application/json"))) {
      console.error(`AJAX request failed: expected application/json response, got ${contentType}`);
      return;
    }

    const cows = await response.json();

    for (const cow of cows) {
      const herdTableTemplate = document.querySelector("template#herd-table-template");
      const entry = herdTableTemplate.content.children[0].cloneNode(true);

      const cowIdContainer = entry.children[0].children[0];
      const cowBirthDateContainer = entry.children[1];

      cowIdContainer.textContent = cow.cow_id;
      cowIdContainer.innerHTML = cow.cow_id;

      if (cow.born_date == null) {
        cowBirthDateContainer.textContent = "Unknown";
        cowBirthDateContainer.innerHTML = "Unknown";
      } else {
        const formattedDate = new Date(cow.born_date).toLocaleDateString("fr-FR", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        cowBirthDateContainer.textContent = formattedDate;
        cowBirthDateContainer.innerHTML = formattedDate;
      }

      herdTable.appendChild(entry);
    }
  } catch (error) {
    console.error(`AJAX request failed due to: ${error}`);
    alert("Impossible de récupérer la liste des vaches.");
  }
}
