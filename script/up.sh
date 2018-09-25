#!/bin/bash
docker build -t py3-opcv3-pil .
docker run -it --rm -v $(pwd):/app py3-opcv3-pil /bin/bash