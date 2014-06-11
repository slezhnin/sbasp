#!/bin/sh

echo Generating test data...
python gen_test_data.py

echo Load test data into database...
python load_data.py

echo Generation reports...
python report_payment.py
