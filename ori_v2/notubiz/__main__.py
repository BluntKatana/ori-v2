# Description: Main file to retrieve data from Notubiz API
import argparse
from ori_v2.logger.logger import Logger
from ori_v2.notubiz.tasks import scrape_events, scrape_agenda_item

log = Logger("notubiz.main").get_logger()

# Define parsing arguments
parser = argparse.ArgumentParser(
        description='Retrieve data from Notubiz API'
    )

parser.add_argument('--organisation_id', '--o', type=int, help='Organization ID inside Notubiz API')
parser.add_argument('--year', type=int, help='Year to retrieve data from')

args = parser.parse_args()

# Start events task
scrape_events.delay(
    organisation_id=args.organisation_id,
    year=args.year,
)

# scrape_agenda_item.delay(
#     meeting_uuid=None,
#     municipality_uuid=None,
#     agenda_url="https://api.notubiz.nl/agenda_items/agenda_points/8825286"
# )
