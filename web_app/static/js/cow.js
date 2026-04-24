window.addEventListener("load", () => {
  console.log(
    document.querySelector("meta[name=cow-info]").getAttribute("content")
  );

  const changeButton = document.querySelector("button#change-button");
  const inseminationButton = document.querySelector("button#insemination-button");
  const removeButton = document.querySelector("button#delete-button");
  const overlay = document.querySelector("div#overlay");

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

        console.log(response);
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

  removeButton.addEventListener("click", async () => {
    const cowId = parseInt(removeButton.getAttribute("cow"));

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
});
