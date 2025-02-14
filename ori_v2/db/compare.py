
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
    documents: List[Document] = get_all(Document)

    # check how many documents have the same id
    print("In Notubiz")
    notubiz_ids = [doc.source_id for doc in documents]
    notubiz_ids = np.unique(notubiz_ids)
    print('Total documents:', len(documents))
    print('Unique ids:', len(notubiz_ids))

    # read in ids from .txt file for comparison
    with open('./ori_v2/db/waddinxveen_ids.txt', 'r') as f:
        ori_ids = np.asarray(f.read().splitlines(), dtype=int)
        print("In ORI")
        print('Total documents:', len(ori_ids))
        print('Unique ids:', len(ori_ids))
        # ori_ids = np.unique(ori_ids)

    # compare the ids
    in_notubiz_not_in_ori = np.setdiff1d(notubiz_ids, ori_ids)
    in_ori_not_in_notubiz = np.setdiff1d(ori_ids, notubiz_ids)

    print('In Notubiz but not in ORI:', len(in_notubiz_not_in_ori))
    print('In ORI but not in Notubiz:', len(in_ori_not_in_notubiz))
