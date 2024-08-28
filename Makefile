# Specify the configuration environment (modify as needed)
CONFIG_ENV=dev
# FLASK_APP='app:create_app("$(CONFIG_ENV)")'

# Init venv & install dependencies
init:
	echo "Initializing virtual environment..."; \
	python3 -m venv env; \
	source env/bin/activate; \
	pip install -r requirements.txt; \
	echo "Done!"

install:
	echo "Installing dependencies..."; \
	pip install -r requirements.txt; \
	echo "Dependencies installed."

clean:
	rm -rf env; \
	echo "Environment deleted"

# Target to run the application
run:
	echo	"Starting Flask application..."; \
	# flask --app $(FLASK_APP) --debug run
	flask run
