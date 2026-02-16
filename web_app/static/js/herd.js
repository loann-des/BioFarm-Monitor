window.addEventListener("load", async () => {
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
