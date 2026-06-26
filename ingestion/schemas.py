from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class TaxiTrip(BaseModel):
    vendor_id: Optional[int] = None
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: Optional[int] = None
    trip_distance: float
    pickup_location_id: int
    dropoff_location_id: int
    payment_type: Optional[int] = None
    fare_amount: float
    tip_amount: float
    total_amount: float
    congestion_surcharge: Optional[float] = None

    @validator("trip_distance")
    def distance_positive(cls, v):
        if v < 0:
            raise ValueError("trip_distance must be >= 0")
        return v

    @validator("fare_amount", "total_amount")
    def amount_positive(cls, v):
        if v < 0:
            raise ValueError("Amounts must be >= 0")
        return v

    @validator("dropoff_datetime")
    def dropoff_after_pickup(cls, v, values):
        if "pickup_datetime" in values and v <= values["pickup_datetime"]:
            raise ValueError("dropoff must be after pickup")
        return v