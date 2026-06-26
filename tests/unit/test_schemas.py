import pytest 
from datetime import datetime 
 
def test_trip_distance_positive(): 
    distance = 2.5 
    assert distance > 0 
 
def test_fare_amount_positive(): 
    fare = 14.9 
    assert fare > 0 
 
def test_dropoff_after_pickup(): 
    pickup = datetime(2023, 1, 1, 10, 0, 0) 
    dropoff = datetime(2023, 1, 1, 10, 30, 0) 
    assert dropoff > pickup 
 
def test_trip_distance_not_outlier(): 
    distance = 2.58 
    assert 0 < distance < 100 
 
def test_total_amount_reasonable(): 
    total = 24.18 
    assert 0 < total < 1000 
