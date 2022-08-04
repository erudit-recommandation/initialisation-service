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