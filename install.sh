#!/bin/bash

cd rabbitvcs-0.19/

sudo python3 setup.py install --install-layout=deb

cd ..
sudo cp rabbitvcs-0.19/clients/nemo/RabbitVCS.py  /usr/share/nemo-python/extensions/RabbitVCS.py
sudo chmod +x /usr/share/nemo-python/extensions/RabbitVCS.py

nemo -q