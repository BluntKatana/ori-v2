from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import (Mapped, backref, declarative_base, mapped_column,
                            relationship)

Base = declarative_base()

class Municipality(Base):
    __tablename__ = 'municipality'

    uuid = Column(String, primary_key=True)

    # municipality-specific
    identifier = Column(String, nullable=False)
    source = Column(String, nullable=False) # e.g. "notubiz", "ibab"

    # meta info
    created_on = Column(DateTime(), default=datetime.now)

    # relations
    # - can contain multiple meetings
    meetings: Mapped[List["Meeting"]] = relationship(back_populates="municipality")
    # - can contain multiple agenda items
    agenda_items: Mapped[List["AgendaItem"]] = relationship(back_populates="municipality")
    # - can contain multiple documents
    documents: Mapped[List["Document"]] = relationship(back_populates="municipality")

class Meeting(Base):
    __tablename__ = 'meeting'

    uuid = Column(String, primary_key=True)

    # meeting-specific
    title  = Column(String, nullable=True)
    source_creation_date = Column(DateTime(), nullable=True)
    source = Column(String, nullable=False) # e.g. "notubiz", "ibab"
    source_id = Column(Integer(), nullable=True) # unique id in source
    source_api_url = Column(String, nullable=True) # api url where we found the meeting
    source_page_url = Column(String, nullable=True) # page url where can find the meeting

    # JSON-blob of the meeting data
    data = Column(Text, nullable=True)

    # meta info
    created_on = Column(DateTime(), default=datetime.now)

    # relation
    # - belongs to a municipality
    municipality_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('municipality.uuid'))
    municipality: Mapped[Optional["Municipality"]] = relationship(back_populates="meetings")
    # - can contain multiple agenda items
    agenda_items: Mapped[List["AgendaItem"]] = relationship(back_populates="meeting")
    # - can contain multiple document
    documents: Mapped[List["Document"]] = relationship(back_populates="meeting")


class AgendaItem(Base):
    __tablename__ = 'agenda_item'

    uuid = Column(String, primary_key=True)

    # agenda item-specific
    title = Column(String, nullable=True)
    source = Column(String, nullable=False) # e.g. "notubiz", "ibab"
    source_id = Column(Integer(), nullable=True) # unique id in source
    source_api_url = Column(String, nullable=True) # api url where we found the agenda item

    # JSON-blob of the agenda item data
    data = Column(Text, nullable=True)

    # meta info
    created_on = Column(DateTime(), default=datetime.now)

    # relation
    # - belongs to a manicipality
    municipality_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('municipality.uuid'))
    municipality: Mapped[Optional["Municipality"]] = relationship(back_populates="agenda_items")
    # - belongs to a meeting
    meeting_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('meeting.uuid'))
    meeting: Mapped[Optional["Meeting"]] = relationship(back_populates="agenda_items")
    # - can contain multiple documents
    documents: Mapped[List["Document"]] = relationship(back_populates="agenda_item")

class Document(Base):
    __tablename__ = 'document'

    uuid = Column(String, primary_key=True)

    # document-specific
    title = Column(String, nullable=True)
    name = Column(String, nullable=True)
    source = Column(String, nullable=False) # e.g. "notubiz", "ibab"
    source_id = Column(Integer(), nullable=True) # unique id in source
    source_api_url = Column(String, nullable=True) # api url where we found the document

    # JSON-blob of the document data
    data = Column(Text, nullable=True)

    # meta info
    created_on = Column(DateTime(), default=datetime.now)

    # relation
    # - can belong to a municipality
    municipality_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('municipality.uuid'))
    municipality: Mapped[Optional["Municipality"]] = relationship(back_populates="documents")
    # - can belong to a meeting
    meeting_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('meeting.uuid'))
    meeting: Mapped[Optional["Meeting"]] = relationship(back_populates="documents")
    # - can belong to an agenda item
    agenda_item_uuid: Mapped[Optional[str]] = mapped_column(ForeignKey('agenda_item.uuid'))
    agenda_item: Mapped[Optional["AgendaItem"]] = relationship(back_populates="documents")

