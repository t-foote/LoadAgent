import os
import sys
import csv
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable
DATABASE_URL = os.environ["DATABASE_URL"]

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

NUMBER_OF_LOADS = int(sys.argv[1]) if (len(sys.argv) > 1) else 20 

def generate_sample_loads():
    """Generate sample load data."""
    cities = [
        ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"),
        ("Houston", "TX"), ("Phoenix", "AZ"), ("Philadelphia", "PA"),
        ("San Antonio", "TX"), ("San Diego", "CA"), ("Dallas", "TX"),
        ("San Jose", "CA")
    ]
    
    equipment_types = ["reefer", "flatbed", "van"]
    commodities = ["electronics", "furniture", "food", "machinery", "clothing"]
    
    loads = []
    base_date = datetime.now()
    
    for _ in range(NUMBER_OF_LOADS):  # Generate 20 sample loads
        origin_city, origin_state = random.choice(cities)
        dest_city, dest_state = random.choice([c for c in cities if c != (origin_city, origin_state)])
        
        # Generate random dates within next 7 days
        pickup_date = base_date + timedelta(days=random.randint(1, 7))
        delivery_date = pickup_date + timedelta(days=random.randint(1, 3))
        
        # Generate random distance between 100 and 2000 miles
        distance = random.randint(100, 2000)
        
        # Generate offer rate based on distance (roughly $2-3 per mile)
        offer_rate = round(distance * random.uniform(2.0, 3.0), 2)
        
        load = {
            "origin_city": origin_city,
            "origin_state": origin_state,
            "dest_city": dest_city,
            "dest_state": dest_state,
            "equipment": random.choice(equipment_types),
            "pickup_ts": pickup_date,
            "distance_mi": distance,
            "offer_rate": offer_rate,
            "created_at": datetime.now()
        }
        loads.append(load)
    
    return loads

def seed_database():
    """Seed the database with sample loads."""
    try:
        # Generate sample loads
        loads = generate_sample_loads()
        
        # Insert loads into database
        for load in loads:
            session.execute(
                text("""
                INSERT INTO loads (
                    origin_city, origin_state, dest_city, dest_state,
                    equipment, pickup_ts, distance_mi, offer_rate, created_at
                ) VALUES (
                    :origin_city, :origin_state, :dest_city, :dest_state,
                    :equipment, :pickup_ts, :distance_mi, :offer_rate, :created_at
                )
                """),
                load
            )
        
        # Refresh the materialized view
        session.execute(text("REFRESH MATERIALIZED VIEW best_load"))
        
        session.commit()
        print("Successfully seeded database with sample loads!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
