#!/bin/bash

app=$(basename $(pwd))
tar czv --exclude=*.pyc --exclude=packaging.sh --exclude=.git --exclude=.gitignore --exclude=env --exclude=local --exclude=tags ../${app} > ../${app}.tar.gz
mv ../${app}.tar.gz ../${app}.spl
