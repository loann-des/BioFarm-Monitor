from datetime import datetime
from icalendar import Calendar, Event

from .models.cow import Cow

def create_drying_event(date_obj: datetime, cows_ids: list[int]) -> Event:
    """Créée un événement iCalendar pour le tarissement des vaches.

    Cette fonction créée un événement iCalendar à la date fourni en argument
    affichant la liste des vaches à tarir ce jour-là.

    Arguments:
        * date_obj (datetime): La date de tarissement des vaches concernées
        * cows (list[Cow]): La liste des vaches à tarir ce jour-là

    Renvoie:
        * icalendar.Event
    """
    event = Event()
    event.add("summary", f"{len(cows_ids)} Tarissement")
    event.add("dtstart", date_obj)
    event.add("dtend", date_obj)
    event.add("dtstamp", date_obj)

    description = str()

    for cow_id in cows_ids:
        description += f"Tarissement de la vache {cow_id}\n"

    event.add("description", description)

    return event

def create_calving_preparation_event(date_obj: datetime, cows_ids: list[int]) -> Event:
    """Créée un événement iCalendar pour le tarissement des vaches.

    Cette fonction créée un événement iCalendar à la date fourni en argument
    affichant la liste des vaches à préparer au vêlage ce jour-là.

    Arguments:
        * date_obj (datetime): La date de préparation au vêlage des vaches
        concernées
        * cows (list[Cow]): La liste des vaches à préparer au vêlage ce jour-là

    Renvoie:
        * icalendar.Event
    """
    event = Event()
    event.add("summary", f"{len(cows_ids)} Préparation au vêlage")
    event.add("dtstart", date_obj)
    event.add("dtend", date_obj)
    event.add("dtstamp", date_obj)

    description = str()

    for cow_id in cows_ids:
        description += f"Préparation au vêlage de la vache {cow_id}\n"

    event.add("description", description)

    return event

def create_calving_event(date_obj: datetime, cows_ids: list[int]) -> Event:
    """Créée un événement iCalendar pour le vêlage des vaches.

    Cette fonction créée un événement iCalendar à la date fourni en argument
    affichant la liste des vaches vêlant ce jour-là.

    Arguments:
        * date_obj (datetime): La date de préparation au vêlage des vaches
        concernées
        * cows (list[Cow]): La liste des vaches vêlant ce jour-là

    Renvoie:
        * icalendar.Event
    """
    event = Event()
    event.add("summary", f"{len(cows_ids)} Vêlage")
    event.add("dtstart", date_obj)
    event.add("dtend", date_obj)
    event.add("dtstamp", date_obj)

    description = str()

    for cow_id in cows_ids:
        description += f"Vêlage de la vache {cow_id}\n"

    event.add("description", description)

    return event

def event_to_fullcalendar(event : Event, color: str):
    return {
        "title": str(event.get("summary")),

        "start": event.get("dtstart").dt.isoformat(),

        "end": event.get("dtend").dt.isoformat(),

        "description": str(event.get("description", "")),

        "color": color,

        "allDay": True
    }
