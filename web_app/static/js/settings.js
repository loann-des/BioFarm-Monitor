let timeoutId = {};

window.addEventListener("load", () => {


    document.querySelectorAll("form").forEach((form) => {

        form.addEventListener("submit", async (e) => {

            e.preventDefault();

            const action = form.getAttribute("action");
            const method = form.getAttribute("method");

            const data = new FormData(form);

            try {

                const response = await fetch(action, {
                    method: method,
                    body: data
                });

                const contentType = response.headers.get("Content-Type");

                if (contentType && contentType.includes("application/json")) {

                    const result = await response.json();

                    const errorContainer =
                        document.querySelector(`#message-div-${result.id}`);

                    const errorTextContainer =
                        document.querySelector(`#message-div-${result.id} span`);

                    clearTimeout(timeoutId[result.id]);

                    errorContainer.classList.remove(
                        "message-div",
                        "error-div",
                        "success-div"
                    );

                    errorContainer.classList.add(
                        result.success ? "success-div" : "error-div"
                    );

                    errorTextContainer.textContent = result.message;

                    timeoutId[result.id] = setTimeout(() => {

                        errorContainer.classList.remove(
                            "error-div",
                            "success-div"
                        );

                        errorContainer.classList.add("message-div");

                    }, 5000);

                } else {

                    window.location = "/";

                }

            } catch (error) {

                console.log(`AJAX request failed due to ${error}`);

            }

        });

    });

});