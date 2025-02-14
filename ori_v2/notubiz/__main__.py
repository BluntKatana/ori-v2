# Description: Main file to retrieve data from Notubiz API
import argparse
import json
import requests
from ori_v2.db.db import Database
from ori_v2.db.schema import Document, Meeting, AgendaItem, Municipality
from ori_v2.logger.logger import Logger
from ori_v2.notubiz.utils import parse_title

log = Logger("notubiz.main").get_logger()

# Define parsing arguments
parser = argparse.ArgumentParser(
        description='Retrieve data from Notubiz API'
    )

parser.add_argument('--organisation_id', '--o', type=int, help='Organization ID inside Notubiz API')
parser.add_argument('--year', type=int, help='Year to retrieve data from')

args = parser.parse_args()

"""
organisation_id: int
year: int
"""
settings = {
    'organisation_id': args.organisation_id,
    'year': args.year
}

dbMunicipality = Municipality(
    uuid=Database.uuid(),
    source="notubiz",
    identifier=settings['organisation_id']
)

# --------
# Retrieve data from meetings
# --------
page = 1
while True:
    url = f'https://api.notubiz.nl/organisation/{settings["organisation_id"]}/meetings?year={settings["year"]}'
    eventsReponse = requests.get(
        url="https://api.notubiz.nl/events",
        params={
            "page": page,
            "organisation_id": settings["organisation_id"],
            "date_from": f"{settings['year']}-01-01 00:00:00",
            "date_to": f"{settings['year']}-12-31 23:59:59",
            "format": "json",
            "version": "1.17.0",
            "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
        }
    )

    db = Database()
    session = db.Session()

    eventsData = eventsReponse.json()


    module_documents = 0
    page = 1
    for event in eventsData['events']:
        if not (event['type'] == 'meeting'):
            log.info("Not a meeting")
            continue
        dbMeeting = Meeting(
            uuid=Database.uuid(), 
            source="notubiz",
            municipality=dbMunicipality
        )
        dbMeeting.source_id = event['id']
        dbMeeting.source_api_url = f"https://{event['event_type_data']['self']}" if event['event_type_data']['self'] else None
        dbMeeting.title = parse_title(event['attributes']) if event['attributes'] else None

        # retrieve meeting data
        meetingResponse = requests.get(
            url=dbMeeting.source_api_url,
            params={
                "format": "json",
                "version": "1.17.0",
                "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
            }
        )

        if meetingResponse.status_code != 200:
            log.warning(f"Error retrieving meeting data: {meetingResponse.status_code}, {dbMeeting.source_api_url}")
            session.add(dbMeeting)
            continue

        meetingData = meetingResponse.json()
        meeting = meetingData['meeting']

        dbMeeting.data = json.dumps(meeting)
        dbMeeting.source_page_url = meeting['url']
        dbMeeting.source_creation_date = meeting['creation_date']

        session.add(dbMeeting)
        session.commit()

        # retrieve all documents under a meeting
        for document in meeting['documents']:
            dbDocument = Document(
                uuid=Database.uuid(),
                source="notubiz",
                municipality=dbMunicipality
            )
            dbDocument.title = document['title']
            dbDocument.source_id = document['id']
            dbDocument.source_api_url = document['url']
            dbDocument.data = json.dumps(document)
            dbDocument.meeting = dbMeeting
            log.info(f"meeting_document: {dbDocument.source_id}, {dbDocument.source_api_url}")
            session.add(dbDocument)
            session.commit()

        # retrieve all agenda_items
        for agenda_item in meeting['agenda_items']:
            if (not agenda_item['type'] == 'agenda_point'):
                log.warning(f"Not an agenda point: {agenda_item['type']}")
                continue

            dbAgendaItem = AgendaItem(
                uuid=Database.uuid(),
                source="notubiz",
                municipality=dbMunicipality
            )

            dbAgendaItem.source_id = agenda_item.get("id", None)
            dbAgendaItem.source_api_url = f"https://{agenda_item['type_data']['self']}" if agenda_item['type_data']['self'] else None
            dbAgendaItem.title = parse_title(event['attributes']) if event['attributes'] else None
            dbAgendaItem.data = json.dumps(agenda_item)
            dbAgendaItem.meeting = dbMeeting

            session.add(dbAgendaItem)
            session.commit()

            # retrieve all documents
            for document in agenda_item['documents']:
                dbDocument = Document(
                    uuid=Database.uuid(),
                    source="notubiz",
                    municipality=dbMunicipality
                )
                dbDocument.title = document['title']
                # dbDocument.name = document['versions'][0]['file_name']
                dbDocument.source_api_url = document['url']
                dbDocument.source_id = document['id']
                if not dbDocument.source_id:
                    log.info(f"No source_id found: {dbModuleDocument.source_api_url}")
                dbDocument.data = json.dumps(document)
                dbDocument.agenda_item = dbAgendaItem
                log.info(f"agenda_document: {dbDocument.source_id}, {dbDocument.source_api_url}")
                session.add(dbDocument)
                session.commit()

            # retrieve all documents from module items
            for module_item in agenda_item['module_items']:
                url = f"https://{module_item['self']}"
                if not url:
                    print("No url on module item found")
                    continue

                moduleItemResponse = requests.get(
                    url=url,
                    params={
                        "format": "json",
                        "version": "1.17.0",
                        "application_token": "11ef5846eaf0242ec4e0bea441379d699a77f703d"
                    }
                )

                if moduleItemResponse.status_code != 200:
                    log.warning(f"Error retrieving module item data: {moduleItemResponse.status_code}, {url}")
                    continue

                moduleItemData = moduleItemResponse.json()
                moduleItem = moduleItemData['item']
                log.info(f"module_item: {moduleItem['id']}")

                attachments = moduleItem.get('attachments', None)
                if not attachments:
                    log.info(f"no attachments found: {moduleItem['id']}")
                    continue

                documents = attachments['document']

                for attachment in documents:
                    dbModuleDocument = Document(
                        uuid=Database.uuid(),
                        source="notubiz",
                        municipality=dbMunicipality
                    )

                    dbModuleDocument.title = attachment['title']
                    dbModuleDocument.source_id = attachment['id']
                    dbModuleDocument.source_api_url = attachment['url']
                    dbModuleDocument.data = json.dumps(attachment)
                    dbModuleDocument.agenda_item = dbAgendaItem
                    if not dbModuleDocument.source_id:
                        log.info(f"no source_id found: {dbModuleDocument.source_api_url}")

                    module_documents += 1
                    log.info(f"module_document: {dbModuleDocument.source_id}, {url}")
                    session.add(dbModuleDocument)
                    session.commit()
    
    if eventsReponse['pagination']['has_more_pages']:
        


log.info(f"Total module documents: {module_documents}")
session.flush()
session.close()