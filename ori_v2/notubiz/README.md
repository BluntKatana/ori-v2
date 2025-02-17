## Structure

# Relational structure found

- Meeting

  - many: documents
  - many: agenda_items
  - many: module_items

- AgendaItem

  - many: documents
  - many: agenda_items (?)
  - many: module_items

- ModuleItem

  - many: documents

- Document
  - many: connections

### Meeting structure

```json
{
  "meeting": {
    "organisation": {
      "id": 505,
      "self": "api.notubiz.nl/organisations/505"
    },
    "gremium": {
      "id": 169,
      "self": "api.notubiz.nl/organisations/505/gremia/169"
    },
    "module_items": [],
    "parent": null,
    "documents": [],
    "folders": [],
    "id": 1152031,
    "self": "api.notubiz.nl/events/meetings/1152031",
    "type": "meeting",
    "permission_group": "public",
    "body": "council",
    "confidential": 0,
    "announcement": false,
    "canceled": false,
    "inactive": false,
    "creation_date": "2023-09-26 15:52:05",
    "last_modified": "2025-02-03 10:44:56",
    "order": null,
    "live": false,
    "archive_state": "unarchived",
    "archive_state_last_modified": null,
    "allow_subscriptions": false,
    "subscriptions": [],
    "url": "https://bunschoten.notubiz.nl/vergadering/1152031/Gemeenteraad",
    "salutation": null,
    "template": false,
    "attributes": [
      {
        "id": 1,
        "reference_model": null,
        "value": "Gemeenteraad"
      },
      {
        "id": 3,
        "reference_model": null,
        "value": "<p>Hierbij wordt u namens de voorzitter uitgenodigd voor de openbare vergadering van de Gemeenteraad</p>\r\n<p>Bij deze vergadering is ondertiteling beschikbaar. U kunt deze aanzetten door in de balk onderaan de videoplayer op \"CC\" te klikken.</p>"
      }
    ],
    "plannings": [
      {
        "start_date": "2024-12-12 19:30:00",
        "end_date": null
      }
    ],
    "agenda_items": [
      {
        "parent": null,
        "meeting": {
          "id": 1152031,
          "self": "api.notubiz.nl/events/meetings/1152031"
        },
        "type_data": {
          "self": "api.notubiz.nl/agenda_items/agenda_points/8825286",
          "heading": false,
          "title_prefix": "1",
          "attributes": [
            {
              "id": 1,
              "reference_model": null,
              "preview": false,
              "value": "Opening"
            }
          ]
        },
        "agenda_items": [],
        "module_items": [],
        "id": 8825286,
        "type": "agenda_point",
        "order": 1,
        "start_offset": "2",
        "end_offset": "177",
        "start_date": null,
        "end_date": null,
        "confidential": 0,
        "permission_group": "public",
        "last_modified": "2024-12-18 09:03:31",
        "documents": [
          {
            "self": "api.notubiz.nl/document/14967224",
            "url": "https://api.notubiz.nl/document/14967224/1",
            "title": "Besluitenlijst Gemeenteraad 12-12-2024",
            "description": "",
            "date": "",
            "case_code": "",
            "policy_field": "",
            "category": "",
            "id": 14967224,
            "confidential": 0,
            "publication_date": "2025-02-12",
            "last_modified": "2024-12-18 09:03:31",
            "version": 1,
            "types": [
              {
                "id": 2,
                "value": "Besluitenlijst"
              }
            ],
            "versions": [
              {
                "type": "file",
                "mime_type": "application/pdf",
                "file_name": "Besluitenlijst_Gemeenteraad_12-12-2024.pdf",
                "file_size": 168876,
                "id": 1
              }
            ],
            "connections": [
              {
                "self": "https://api.notubiz.nl/document/14967224/1/connections/1/8825286",
                "version": 1,
                "order": 1,
                "document_id": 14967224,
                "connection_type": 1,
                "connection_id": 8825286
              }
            ]
          }
        ]
      }
    ]
  }
}
```

# Noteworthy

Each meeting has several parts:

- documents
- agenda items
- module items

- Each type has attributes where:
  - id = 1, value: <title>
