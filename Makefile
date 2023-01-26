
WORKDIR=$(shell echo $$PWD)
VENV_BIN=$(WORKDIR)/venv/bin

.DEFAULT_GOAL := help

virtualenv:
	@if [[ ! -d $(WORKDIR)/venv ]]; then \
		virtualenv $(WORKDIR)/venv; \
	fi

install-requirements:	virtualenv
	@if [[ ! -f $(WORKDIR)/venv/done ]]; then \
		. $(VENV_BIN)/activate;  pip install -r pip.txt; \
		. $(VENV_BIN)/activate; ansible-galaxy collection install -r requirements.yml; \
		touch $(WORKDIR)/venv/done; \
	fi


#? deploy-all:	Run's all the targets
deploy-all:	install-requirements
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t all -e @vars.yaml 

#? build:		Build and Push Container Images
build:	install-requirements
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t build -e @vars.yaml 

#? nfd:			Deploy NFD operator
nfd:	install-requirements
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t nfd -e @vars.yaml

#? gpu:			Deploy Nvidia GPU operator
gpu:	install-requirements
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t gpu -e @vars.yaml

#? vgpu:		Configure vGPU; requires GPU Operator
vgpu:	install-requirements
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t vgpu -e @vars.yaml 

#? kubevirt:	Update Openshift Virtualization for vGPU
kubevirt:
	. $(VENV_BIN)/activate; $(VENV_BIN)/ansible-playbook -i localhost, playbook.yaml -t kubevirt -e @vars.yaml 

help:
	@echo "Usage:  make [ COMMAND ]"; 	echo ''; echo "COMMANDS:"
	@grep '#?' Makefile | head -n -1 | awk -F '?' '{ print $$2}'
