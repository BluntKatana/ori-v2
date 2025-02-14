import json
import requests

from ori_v2.db.db import Database
from ori_v2.db.schema import AgendaItem, Document, Meeting, Municipality
from ori_v2.logger.logger import Logger
from ori_v2.notubiz.utils import parse_title
from ..celery import app

log = Logger("notubiz.main").get_logger()

@app.task
def scrape_events(organisation_id: int, year: int):
    """
    Scrape events from the Notubiz API

    Params:
        organisation_id (int): The organisation ID to scrape
        year (int): The year to scrape

    Returns:
        None
    """
    db = Database()
    session = db.Session()
    dbMunicipality = Municipality(
        uuid=Database.uuid(),
        source="notubiz",
        identifier=organisation_id
    )

    session.add(dbMunicipality)
    session.commit()

    url = f'https://api.notubiz.nl/events'
    eventsReponse = requests.get(
        url=url,
        params={
            "organisation_id": organisation_id,
            "date_from": f"{year}-01-01 00:00:00",
            "date_to": f"{year}-12-31 23:59:59",
            "format": "json",
            "version": "1.17.0",
            "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
        }
    )
    print(eventsReponse)



    eventsData = eventsReponse.json()

    for event in eventsData['events']:
        if not (event['type'] == 'meeting'):
            log.info("Not a meeting")
            continue

        meeting_url = f"https://{event['event_type_data']['self']}" if event['event_type_data']['self'] else None
        if not meeting_url:
            log.warning("No meeting URL found for event")
            continue

        scrape_event.delay(dbMunicipality.uuid, meeting_url)
    session.commit()

@app.task
def scrape_event(municipality_uuid: str, meeting_url: str):
    """
    Scrape a single event from the Notubiz API

    Params:
        municipality (Municipality): The municipality connected to the event
        url (str): The URL to scrape

    Returns:
        None
    """
    db = Database()
    session = db.Session()

    meetingResponse = requests.get(
        url=meeting_url,
        params={
            "format": "json",
            "version": "1.17.0",
            "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
        }
    )
    if meetingResponse.status_code != 200:
        log.warning(f"Error retrieving meeting data: {meetingResponse.status_code}, {meeting_url}")
        return

    meetingData = meetingResponse.json()
    meeting = meetingData['meeting']

    log.info(f"Scraping meeting: {meeting['id']}")

    dbMeeting = Meeting(
        uuid=Database.uuid(),
        source="notubiz",
        municipality_uuid=municipality_uuid,
        data=json.dumps(meetingData),
        title=parse_title(meeting['attributes']) if meeting['attributes'] else None,
        source_id=str(meeting['id']),
        source_api_url=meeting_url,
        source_page_url=meeting['url'],
        source_creation_date=meeting['creation_date']
    )
    session.add(dbMeeting)

    # retrieve all documents under a meeting
    for document in meeting['documents']:
        dbDocument = Document(
            uuid=Database.uuid(),
            source="notubiz",
            municipality_uuid=municipality_uuid,
            data=json.dumps(document),
            title=document['title'],
            source_id=str(document['id']),
            source_api_url=document['url'],
            meeting=dbMeeting,
        )
        session.add(dbDocument)

    # retrieve all agenda items under a meeting
    for agenda_item in meeting['agenda_items']:
        scrape_agenda_item.delay(
            dbMeeting.municipality_uuid, 
            dbMeeting.uuid, 
            f"https://{agenda_item['type_data']['self']}"
        )
    session.commit()

@app.task
def scrape_agenda_item(municipality_uuid: str, meeting_uuid: str, agenda_url: str):
    """
    Scrape a single agenda item from the Notubiz API

    Params:
        meeting (Meeting): The meeting connected to the agenda item
        agenda_url (str): The URL to scrape

    Returns:
        None
    """
    db = Database()
    session = db.Session()

    agendaResponse = requests.get(
        url=agenda_url,
        params={
            "format": "json",
            "version": "1.17.0",
            "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
        }
    )
    if agendaResponse.status_code != 200:
        log.warning(f"Error retrieving agenda data: {agendaResponse.status_code}, {agenda_url}")
        return

    agendaData = agendaResponse.json()
    agenda = agendaData['agenda_point']

    dbAgendaItem = AgendaItem(
        uuid=Database.uuid(),
        source="notubiz",
        municipality_uuid=municipality_uuid,
        meeting_uuid=meeting_uuid,
        data=json.dumps(agendaData),
        title=parse_title(agenda['type_data']['attributes']) if agenda['type_data']['attributes'] else None,
        source_id=str(agenda['id']),
        source_api_url=agenda_url,
    )
    session.add(dbAgendaItem)

    # retrieve all documents under an agenda item
    for document in agenda['documents']:
        dbDocument = Document(
            uuid=Database.uuid(),
            source="notubiz",
            municipality_uuid=municipality_uuid,
            agenda_item=dbAgendaItem,
            data=json.dumps(document),
            title=document['title'],
            source_id=str(document['id']),
            source_api_url=document['url'],
        )
        session.add(dbDocument)

    # retrieve all module items under an agenda item
    for module_item in agenda['module_items']:
        module_url = f"https://{module_item['self']}"
        if not module_url:
            log.warning("No module URL found for module item")
            continue
        scrape_module_item.delay(
            dbAgendaItem.municipality_uuid,
            dbAgendaItem.uuid,
            f"https://{module_item['self']}"
        )

    # retrieve all agenda items under an agenda item
    for nested_agenda_item in agenda['agenda_items']:
        if not nested_agenda_item['type'] == 'agenda_point':
            log.info("Not an agenda point")
            continue
        scrape_agenda_item.delay(
            dbAgendaItem.municipality_uuid,
            dbAgendaItem.meeting_uuid,
            f"https://{nested_agenda_item['self']}"
        )
    session.commit()

@app.task
def scrape_module_item(municipality_uuid: str, agenda_item_uuid: str, module_url: str):
    """
    Scrape a single module item from the Notubiz API

    Params:
        agenda_item (AgendaItem): The agenda item connected to the module item
        module_url (str): The URL to scrape

    Returns:
        None
    """
    db = Database()
    session = db.Session()

    moduleResponse = requests.get(
        url=module_url,
        params={
            "format": "json",
            "version": "1.17.0",
            "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
        }
    )
    if moduleResponse.status_code != 200:
        log.warning(f"Error retrieving module data: {moduleResponse.status_code}, {module_url}")
        return

    moduleData = moduleResponse.json()
    moduleItem = moduleData['item']

    attachments = moduleItem.get('attachments', None)
    if not attachments:
        log.warning(f"No attachments found for module item: {agenda_item_uuid}")
        return

    # retrieve all documents under a module item
    for document in attachments['documents']:
        dbDocument = Document(
            uuid=Database.uuid(),
            source="notubiz",
            municipality_uuid=municipality_uuid,
            agenda_item_uuid=agenda_item_uuid,
            data=json.dumps(document),
            title=document['title'],
            source_id=str(document['id']),
            source_api_url=document['url'],
        )
        session.add(dbDocument)
    session.commit()