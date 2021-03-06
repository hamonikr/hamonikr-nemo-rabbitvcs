#!/bin/sh

LOCALE=$1

if [ -z "$LOCALE" ]
then
    echo "usage: ./initialize_new_translation.sh LOCALE"
    exit 1
fi

msginit --input=../po/RabbitVCS.pot --locale=$LOCALE \
    --output-file=../po/$LOCALE.po

echo ""
echo "Once you have translated the strings, install the strings with \
the install_translations.sh script"
