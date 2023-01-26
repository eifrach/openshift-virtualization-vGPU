#!/usr/bin/env python
from sys import argv
from os import path


if len(argv) < 2:
    print(f"ERROR: Usage {argv[0]} <string>")
    exit(1)


FILE=list((path.basename(argv[1])).split('-'))

for i, _ in enumerate(FILE):
    if FILE[i] == "x86_64":
        break

print(FILE[i+1])



