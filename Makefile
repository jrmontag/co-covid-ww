VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

data-update: $(VENV)/bin/activate
	echo 'TODO'

run: $(VENV)/bin/activate
	$(PYTHON) main.py

clean-data: 
	rm data/*.log
	rm data/*.json
	rm data/*.db

clean-env:
	rm -rf __pycache__
	rm -rf $(VENV)

deep-clean: clean-data clean-env 
	

.PHONY: run clean-data clean-env deep-clean
