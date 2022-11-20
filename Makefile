VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: $(VENV)/bin/activate
	$(PYTHON) main.py

db-and-run: $(VENV)/bin/activate
	$(PYTHON) main.py --build_db

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

clean: 
	rm data/*.flat.json
	rm data/*.db

deep-clean:
	rm -rf __pycache__
	rm -rf $(VENV)

.PHONY: run db-and-run clean deep-clean
