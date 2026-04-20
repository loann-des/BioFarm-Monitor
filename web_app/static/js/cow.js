window.addEventListener("load", () => {
  console.log(
    document.querySelector("meta[name=cow-info]").getAttribute("content")
  );

  const changeButton = document.querySelector("button#change-button");
  const removeButton = document.querySelector("button#delete-button");
  const overlay = document.querySelector("div#overlay");
  const popup = document.querySelector("div.popup");
  const popupCloseButton = document.querySelector("div.popup div.popup-header button");

  changeButton.addEventListener("click", async () => {
    overlay.style.display = "block";
    popup.style.display = "block";
  });

  popupCloseButton.addEventListener("click", async () => {
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
    } catch (error) {
      console.error(`AJAX request failed due to ${error}`);
    }

    location.reload()
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
