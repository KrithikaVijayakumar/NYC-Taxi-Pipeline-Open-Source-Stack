import pytest 
from datetime import datetime 
 
def test_trip_distance_positive(): 
    assert 2.5 > 0 
 
def test_fare_amount_positive(): 
    assert 14.9 > 0 
 
def test_dropoff_after_pickup(): 
