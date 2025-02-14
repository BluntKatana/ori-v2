from datetime import datetime
from schema import Meeting, Document
from db import Database


if __name__ == "__main__":
    db = Database()
    session = db.Session()

    meeting1 = Meeting(
        uuid=Database.uuid(),
        title="My first meeting",
        source="notubiz",
        documents=[
            Document(
                uuid=Database.uuid(),
                name="my first document",
                source="notubiz",
            )
        ]
    )

    session.add(meeting1)
    session.commit()
    session.flush()
    print("Meeting added")

    # retrieve the meeting and document
    meetings = session.query(Meeting).filter_by(title="My first meeting").all()
    for meeting in meetings:
        print(meeting.uuid, meeting.title)
        for doc in meeting.documents:
            print(doc.uuid, doc.name)