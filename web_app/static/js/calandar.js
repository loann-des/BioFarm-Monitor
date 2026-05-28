document.addEventListener("DOMContentLoaded", async () => {

    const response = await fetch("/reproduction/calandar/calendar-data");

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

    const events = result.message;

    const calendarEl = document.getElementById("calendar");

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        locale: "fr",
        events: events,
        eventClick(info) {
            alert(
                info.event.extendedProps.description
            );
        }
    }
    );

    calendar.render();
});