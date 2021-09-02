#! /bin/env python

# Simple script which loops and waits

import time

for i in range(10):
    time.sleep(2)
    print(f'Step {i}')

