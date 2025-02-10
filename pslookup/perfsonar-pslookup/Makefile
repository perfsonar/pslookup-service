#
# Makefile for python-lookup-service-client module
#

default: build

build:
	python3 setup.py build

install:
ifndef PERFSONAR-ROOTPATH
	@echo No PERFSONAR-ROOTPATH specified for installation
	@false
endif
ifndef PERFSONAR-CONFIGPATH
	@echo No PERFSONAR-CONFIGPATH specified for installation
	@false
endif
ifndef PYTHON-ROOTPATH
	@echo No PYTHON-ROOTPATH specified for installation
	@false
endif
ifndef PERFSONAR-DATAPATH
	@echo No PERFSONAR-DATAPATH specified for installation
	@false
endif
ifndef BINPATH
	@echo No BINPATH specified for installation
	@false
endif
	python3 setup.py install --root=${PYTHON-ROOTPATH} -O1 --record=INSTALLED_FILES
	mkdir -p ${PERFSONAR-ROOTPATH}/bin
	mkdir -p ${PERFSONAR-CONFIGPATH} 
	mkdir -p ${PERFSONAR-CONFIGPATH}/pslookup-record-conf
	mkdir -p ${PERFSONAR-DATAPATH} 
	mkdir -p ${BINPATH}
	install -m 0755 bin/pslookup* ${PERFSONAR-ROOTPATH}/bin
	install -m 0644 pslookup-config/pslookup-record-conf/* ${PERFSONAR-CONFIGPATH}/pslookup-record-conf
	install -m 0644 pslookup-config/*.conf ${PERFSONAR-CONFIGPATH}

clean:
	find . -name "*.pyc" | xargs rm -f
	python3 setup.py clean --all