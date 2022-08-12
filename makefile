run:
	python main.py -d
run-deploy:
	python main.py -p

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

