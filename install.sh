#!/bin/bash

cd rabbitvcs-0.19/

# 최신 리눅스에서 setup.py install 경고를 방지하기 위해 pip 사용
# pip install . --user 방식으로 사용자 디렉토리에 설치
echo "RabbitVCS를 설치합니다..."

# pip가 설치되어 있는지 확인
if command -v pip3 >/dev/null 2>&1; then
    echo "pip3를 사용하여 설치합니다..."
    pip3 install . --user
elif command -v python3 -m pip >/dev/null 2>&1; then
    echo "python3 -m pip을 사용하여 설치합니다..."
    python3 -m pip install . --user
else
    echo "pip가 설치되어 있지 않습니다. 시스템 패키지로 설치합니다..."
    # 기존 방식으로 fallback (권한 문제 해결)
    python3 setup.py install --install-layout=deb --user
fi

cd ..
sudo cp rabbitvcs-0.19/clients/nemo/RabbitVCS.py  /usr/share/nemo-python/extensions/RabbitVCS.py
sudo chmod +x /usr/share/nemo-python/extensions/RabbitVCS.py

nemo -q

echo "설치가 완료되었습니다."