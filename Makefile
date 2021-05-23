all: buildmo

buildmo:
	@echo "Building the mo files"
	# WARNING: the second sed below will only works correctly with the languages that don't contain "-"
	for file in `ls rabbitvcs-0.18/po/*.po`; do \
		lang=`echo $$file | sed 's@po/@@' | sed 's/.po//' | sed 's/rabbitvcs-0.18\///'`; \
		install -d rabbitvcs-0.18/locale/$$lang/LC_MESSAGES/; \
		msgfmt -o rabbitvcs-0.18/locale/$$lang/LC_MESSAGES/RabbitVCS.mo $$file; \
	done \

clean:
	rm -rf rabbitvcs-0.18/locale
	rm -f install