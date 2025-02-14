import argparse
from typing import List
import jq
import numpy as np
import requests

from ori_v2.db.db import Database
from ori_v2.db.schema import Document, Municipality, Meeting, AgendaItem

# Example how to use this script
# - first run:
# poetry run python ./ori_v2/notubiz --organisation_id 1723 --year 2024
# - then compare:
# poetry run python ./ori_v2/notubiz/compare.py --year 2024 --ori_index ori_fixed_waddinxveen_20230709081033 --organisation_id 1723

# Define parsing arguments
parser = argparse.ArgumentParser(
        description='Retrieve data from Notubiz API'
    )

parser.add_argument('--ori_index', type=str, help='Org ID inside openraadsinformatie (e.g. "fixed_waddinxveen_20230709081033")')
parser.add_argument('--organisation_id', '--o', type=int, help='Organization ID inside Notubiz API (e.g. 1)')
parser.add_argument('--year', type=int, help='Year to retrieve data from')

args = parser.parse_args()

settings = {
    'ori_index': str(args.ori_index),
    'organisation_id': args.organisation_id,
    'year': args.year
}

# ----
# Retrieve document data from Openraadsinformatie
# ----

oriResponse = requests.get(
    url="https://api.openraadsinformatie.nl/v1/elastic/_search",
    headers={'Content-Type': 'application/json'},
    json={
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "must": [
                                {
                                    "bool": {
                                        "must": [
                                            {
                                                "simple_query_string": {
                                                    "fields": [
                                                        "text",
                                                        "title",
                                                        "description",
                                                        "name"
                                                    ],
                                                    "default_operator": "OR",
                                                    "query": "*"
                                                }
                                            },
                                            {
                                                "terms": {
                                                    "_index": [
                                                        "ori_*",
                                                        "osi_*",
                                                        "owi_*"
                                                    ]
                                                }
                                            },
                                            {
                                                "term": {
                                                    "@type": "MediaObject"
                                                }
                                            }
                                        ],
                                        "must_not": [
                                            {
                                                "match": {
                                                    "@type": "Membership"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "terms": {
                                                    "_index": [
                                                        settings['ori_index']
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "range": {
                                        "last_discussed_at": {
                                            "gte": f"{settings['year']}-01-01T00:00:00",
                                            "lte": f"{settings['year']}-12-31T23:59:59",
                                            "boost": 2
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "highlight": {
            "pre_tags": [
                "<mark>"
            ],
            "post_tags": [
                "</mark>"
            ],
            "fields": {
                "text": {},
                "title": {},
                "name": {},
                "description": {}
            },
            "fragment_size": 100,
            "number_of_fragments": 3
        },
        "size": 1000,
        "_source": {
            "includes": [
                "was_generated_by.reference_identifier"
            ],
            "excludes": []
        },
        "aggs": {
            "_index": {
                "terms": {
                    "field": "_index",
                    "size": 1000,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        },
        "from": 0,
        "sort": [
            {
                "last_discussed_at": {
                    "order": "desc"
                }
            }
        ]
    }
)
oriData = oriResponse.json()
ori_ids = jq.compile('.hits.hits | map(._source.was_generated_by.reference_identifier | tonumber)').input(oriData).first()

# ---
# Retrieve documents from Notubiz (parsed before hand)
# ---
municipality: Municipality = Database().Session()\
    .query(Municipality)\
    .where(Municipality.identifier == str(settings['organisation_id']))\
    .first()

documents: List[Document] = Database().Session()\
    .query(Document)\
    .where(Document.municipality_uuid == municipality.uuid)

notubiz_ids = [doc.source_id for doc in documents]
notubiz_ids = np.unique(notubiz_ids)

# ---
# Compare the ids
# ---

in_notubiz_not_in_ori = np.setdiff1d(notubiz_ids, ori_ids)
in_ori_not_in_notubiz = np.setdiff1d(ori_ids, notubiz_ids)

print("-- Documents --")
print('Scraped from Notubiz:', len(notubiz_ids))
print('Scraped from ORI:', len(ori_ids))

print('In Notubiz but not in ORI:', len(in_notubiz_not_in_ori))
print('In ORI but not in Notubiz:', len(in_ori_not_in_notubiz))

# ---
# Compare meetings
# ---

agendaItemsResponse = requests.get(
    url="https://api.openraadsinformatie.nl/v1/elastic/_search",
    headers={'Content-Type': 'application/json'},
    json={
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "must": [
                                {
                                    "bool": {
                                        "must": [
                                            {
                                                "simple_query_string": {
                                                    "fields": [
                                                        "text",
                                                        "title",
                                                        "description",
                                                        "name"
                                                    ],
                                                    "default_operator": "OR",
                                                    "query": "*"
                                                }
                                            },
                                            {
                                                "terms": {
                                                    "_index": [
                                                        "ori_*",
                                                        "osi_*",
                                                        "owi_*"
                                                    ]
                                                }
                                            },
                                            {
                                                "term": {
                                                    "@type": "Meeting"
                                                }
                                            }
                                        ],
                                        "must_not": [
                                            {
                                                "match": {
                                                    "@type": "Membership"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "terms": {
                                                    "_index": [
                                                        settings['ori_index']
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "range": {
                                        "last_discussed_at": {
                                            "gte": f"{settings['year']}-01-01T00:00:00",
                                            "lte": f"{settings['year']}-12-31T23:59:59",
                                            "boost": 2
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "highlight": {
            "pre_tags": [
                "<mark>"
            ],
            "post_tags": [
                "</mark>"
            ],
            "fields": {
                "text": {},
                "title": {},
                "name": {},
                "description": {}
            },
            "fragment_size": 100,
            "number_of_fragments": 3
        },
        "size": 1000,
        "_source": {
            "includes": [
                "was_generated_by.original_identifier"
            ],
            "excludes": []
        },
        "aggs": {
            "_index": {
                "terms": {
                    "field": "_index",
                    "size": 1000,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        },
        "from": 0,
        "sort": [
            {
                "last_discussed_at": {
                    "order": "desc"
                }
            }
        ]
    }
)
agendaItemsData = agendaItemsResponse.json()
ori_agenda_items_ids = jq.compile('.hits.hits | map(._source.was_generated_by.original_identifier | tonumber)').input(agendaItemsData).first()


agenda_items: List[Meeting] = Database().Session()\
    .query(Meeting)\
    .where(Meeting.municipality_uuid == municipality.uuid)

notubiz_agenda_ids = [meeting.source_id for meeting in agenda_items]
notubiz_agenda_ids = np.unique(notubiz_agenda_ids)

in_notubiz_not_in_ori = np.setdiff1d(notubiz_agenda_ids, ori_agenda_items_ids)
in_ori_not_in_notubiz = np.setdiff1d(ori_agenda_items_ids, notubiz_agenda_ids)

print("-- Meetings --")
print('Scraped from Notubiz:', len(notubiz_agenda_ids))
print('Scraped from ORI:', len(ori_agenda_items_ids))

print('In Notubiz but not in ORI:', len(in_notubiz_not_in_ori))
print('In ORI but not in Notubiz:', len(in_ori_not_in_notubiz))


# ---
# Compare agenda items
# ---

agendaItemsResponse = requests.get(
    url="https://api.openraadsinformatie.nl/v1/elastic/_search",
    headers={'Content-Type': 'application/json'},
    json={
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "must": [
                                {
                                    "bool": {
                                        "must": [
                                            {
                                                "simple_query_string": {
                                                    "fields": [
                                                        "text",
                                                        "title",
                                                        "description",
                                                        "name"
                                                    ],
                                                    "default_operator": "OR",
                                                    "query": "*"
                                                }
                                            },
                                            {
                                                "terms": {
                                                    "_index": [
                                                        "ori_*",
                                                        "osi_*",
                                                        "owi_*"
                                                    ]
                                                }
                                            },
                                            {
                                                "term": {
                                                    "@type": "AgendaItem"
                                                }
                                            }
                                        ],
                                        "must_not": [
                                            {
                                                "match": {
                                                    "@type": "Membership"
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "terms": {
                                                    "_index": [
                                                        settings['ori_index']
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "range": {
                                        "last_discussed_at": {
                                            "gte": f"{settings['year']}-01-01T00:00:00",
                                            "lte": f"{settings['year']}-12-31T23:59:59",
                                            "boost": 2
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "highlight": {
            "pre_tags": [
                "<mark>"
            ],
            "post_tags": [
                "</mark>"
            ],
            "fields": {
                "text": {},
                "title": {},
                "name": {},
                "description": {}
            },
            "fragment_size": 100,
            "number_of_fragments": 3
        },
        "size": 1000,
        "_source": {
            "includes": [
                "was_generated_by.reference_identifier"
            ],
            "excludes": []
        },
        "aggs": {
            "_index": {
                "terms": {
                    "field": "_index",
                    "size": 1000,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        },
        "from": 0,
        "sort": [
            {
                "last_discussed_at": {
                    "order": "desc"
                }
            }
        ]
    }
)
agendaItemsData = agendaItemsResponse.json()
ori_agenda_items_ids = jq.compile('.hits.hits | map(._source.was_generated_by.reference_identifier | tonumber)').input(agendaItemsData).first()


agenda_items: List[AgendaItem] = Database().Session()\
    .query(AgendaItem)\
    .where(AgendaItem.municipality_uuid == municipality.uuid)

notubiz_agenda_ids = [meeting.source_id for meeting in agenda_items]
notubiz_agenda_ids = np.unique(notubiz_agenda_ids)

in_notubiz_not_in_ori = np.setdiff1d(notubiz_agenda_ids, ori_agenda_items_ids)
in_ori_not_in_notubiz = np.setdiff1d(ori_agenda_items_ids, notubiz_agenda_ids)

print("-- Agenda Items --")
print('Scraped from Notubiz:', len(notubiz_agenda_ids))
print('Scraped from ORI:', len(ori_agenda_items_ids))

print('In Notubiz but not in ORI:', len(in_notubiz_not_in_ori))
print('In ORI but not in Notubiz:', len(in_ori_not_in_notubiz))

