window.addEventListener("load", () => {
    
    let timeoutId;
    const loginForm = document.querySelector("form");
    loginForm.addEventListener("submit", async (e) => {
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
            
            if (contentType.includes("application/json")) {
                const result = await response.json();
                const errorContainer = document.querySelector(`div#message-div-${result.id}`);
                const errorTextContainer = document.querySelector(`div#message-div-${result.id} span`);

                clearTimeout(timeoutId); // Clear any existing timeout to prevent multiple timers

                // afficher le message de succès ou d'erreur dans le bons styles
                errorContainer.classList.remove("message-div", "error-div", "success-div");
                errorContainer.classList.add(result.success ? "success-div" : "error-div");

                if (result.success) {
                console.log(result.message);
                } else {
                console.log(result.message);
                }
                // Afficher le message dans le conteneur
                errorTextContainer.textContent = result.message;
                errorTextContainer.innerHTML = result.message;

                // Timer pour masquer le message après 5 secondes
                timeoutId = setTimeout(() => {
                    errorContainer.classList.remove("error-div", "success-div");
                    errorContainer.classList.add("message-div");
                    }, 5000);

            } else {
                window.location = "/";
            }
        } catch (error) {
            console.log(`AJAX request failed due to ${error}`);

            errorTextContainer.textContent = "Impossible de mettre à jour les paramètres";
            errorTextContainer.innerHTML = "Impossible de mettre à jour les paramètres";
            errorContainer.style.display = "block";
        }
    });
});
