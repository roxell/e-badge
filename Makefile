MPREMOTE = uvx mpremote
PERSONAL = personal.txt

upload-badge:
	$(MPREMOTE) fs rm :/examples/badge.py 2>/dev/null; true
	$(MPREMOTE) fs cp badge.py :/examples/badge.py

upload-img:
	$(MPREMOTE) fs rm :/badges/badge.jpg 2>/dev/null; true
	$(MPREMOTE) fs cp badges/badge.jpg :/badges/badge.jpg

upload-jokes:
	$(MPREMOTE) fs cp jokes.txt :/jokes.txt

upload-personal:
	$(MPREMOTE) fs rm :/badges/personal.txt 2>/dev/null; true
	$(MPREMOTE) fs cp $(PERSONAL) :/badges/personal.txt

upload-config:
	$(MPREMOTE) fs cp $(CONF) :/badges/badge.txt

upload-all: upload-badge upload-img upload-jokes upload-personal

reset:
	$(MPREMOTE) reset
