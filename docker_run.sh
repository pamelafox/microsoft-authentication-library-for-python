#!/usr/bin/bash
IMAGE_NAME=msal:latest

docker build -t $IMAGE_NAME - < Dockerfile

echo "=== Integration Test for Python 3.14 which has no AppImage yet ==="
echo "After seeing the bash prompt, run the following to test:"
echo "    pip install -e ."
echo "    pytest --capture=no -s tests/chosen_test_file.py"
docker run --rm -it \
    --privileged \
    -w /home -v $PWD:/home \
    $IMAGE_NAME \
    $@

