import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# set database url
DATABASE_URL='postgres://ntsawgrtysnkkd:8c3dffd059425157b4b6d56e06b121433007f85265d048372cf2e6becf9acbb2@ec2-52-45-73-150.compute-1.amazonaws.com:5432/d9f2s1f41d4egh'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

parks = open ("parks.csv")
reader = csv.reader(parks)
for id, geom, STATUS, DESCRIPTION, FENCING_INFO, PARCEL_LOCATION, lat, lng  in reader:
    db.execute("INSERT INTO parks (id, geom, STATUS, DESCRIPTION, FENCING_INFO, PARCEL_LOCATION, lat, lng) VALUES (:id, :geom, :STATUS, :DESCRIPTION, :FENCING_INFO, :PARCEL_LOCATION, :lat, :lng)",
    {"id": id, "geom": geom, "STATUS": STATUS, "DESCRIPTION": DESCRIPTION, "FENCING_INFO": FENCING_INFO, "PARCEL_LOCATION": PARCEL_LOCATION, "lat": lat, "lng": lng})
print("import success")

db.commit()
