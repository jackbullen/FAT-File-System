#!/usr/bin/env python3
from os import walk, system
for dir,_,files in walk('./'):
    if dir != './':
        continue
    for file in files:
        if file.endswith('.py'):
            system(f'./diskput p3.img {file} /{file}')