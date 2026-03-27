window.addEventListener("load", () => {
  const removeButton = document.querySelector("button#delete-button");

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
