run-docker:
	docker run -it -p 8092:8092 initialisation_service

create-docker:
	docker build -t initialisation_service .
run:
	python main.py -d
	
run-deploy:
	python main.py -p

run-inside-docker:
	python main.py -dd

run-bash-docker:
	docker run --rm -it --entrypoint bash initialisation_service

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

