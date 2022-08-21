run:
	python main.py -d
run-deploy:
	python main.py -p

run-inside-docker-local:
	python main.py -dd

create-docker:
	docker build -t initialisation_service .
run-docker:
	docker run -it  initialisation_service --volume=$(pwd)/data:/app/data

create-docker-local:
	docker build -t  initialisation_service_local -f ./Dockerfile-local .

run-docker-local:
	docker run -it  --volume=$(pwd)/data:/app/data --add-host=host.docker.internal:host-gateway  initialisation_service_local

install:
	pip install -r requirement.txt
	python -m spacy download fr_core_news_sm
	python init.py
	cd sompy && python setup.py install

install-conda:
	conda create -n initialisation_service pip
	pip install -r requirement.txt
	python -m spacy download fr_core_news_sm
	python init.py
	cd sompy && python setup.py install

