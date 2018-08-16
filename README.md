# development-todo
development-todo is a program used to search through directories on the local machine and extract @TODO tags from a code base to create a task list and help developers stay on track.

## Example
./file.py
``` python
#!usr/bin/env python3
@TODO Fix output Formatting

import sys
...
``` 

todo ./
``` 
File        Line#   Comment
./file.py     2     Fix output Formatting 
```

## Options
``` 
-h, --help      show this help message and exit
-i IGNORE       Ignore files with a certain extentsions
-t MAX_THREADS  Define max threads (Default: 6)
-v              Give Verbose output
``` 
