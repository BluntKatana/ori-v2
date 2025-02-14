
import json
from typing import List
from ori_v2.db.db import Database
from ori_v2.db.schema import AgendaItem, Document, Meeting
import numpy as np

from ori_v2.logger.logger import Logger

log = Logger("db.query").get_logger()

def get_all(table) -> list:
    session = Database().Session()
    return session.query(table).all()

if __name__ == "__main__":
    # events: List[Meeting] = get_all(Meeting)
    # for event in events:
        # print(event.source_api_url)
    # print('Total events:', len(events))

    documents: List[Document] = get_all(Document)

    # check how many documents have the same id
    ids = [doc.source_id for doc in documents]
    print('Total documents:', len(documents))
    print('Unique ids:', len(np.unique(ids)))
    print('Unique source_api_urls:', len(np.unique([doc.source_api_url for doc in documents])))

    # print out the data of the documents
    # for doc in documents:
        # log.info(f"Document {doc.source_id}: {json.loads(doc.data)}")

    # retrieve all documents with the same id
    # for id in np.unique(ids):
    #     docs_with_id = [doc for doc in documents if doc.source_id == id]
    #     if len(docs_with_id) > 1:
    #         diff_hashes = len(np.unique([hash(doc.data) for doc in docs_with_id]))
    #         print('Documents with id:', id)
    #         # check whether a hash of the doc.data are equal
    #         hashes = [hash(doc.data) for doc in docs_with_id]
    #         unique_hashes = len(np.unique(hashes))
    #         if unique_hashes > 1:
    #             for doc in docs_with_id:
    #                 print(doc.data)
    #         print('---')

    # retrieve all meetings with the same id
    # meetings: List[Meeting] = get_all(Meeting)
    # ids = [meeting.source_id for meeting in meetings]
    # print('Total meetings:', len(meetings))
    # print('Unique ids:', len(np.unique(ids)))

    # # retrieve all agendaitems with the same id
    # agendaitems: List[AgendaItem] = get_all(AgendaItem)
    # ids = [agendaitem.source_id for agendaitem in agendaitems]
    # print('Total agendaitems:', len(agendaitems))
    # print('Unique ids:', len(np.unique(ids)))
