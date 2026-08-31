# SPDX-License-Identifier: MIT
# Minimal root dispatcher included in the G2 community source archive.

MAKE ?= make

.PHONY: help g2-community-preflight g2-community-local-build

help:
	@echo 'openCFW G2 community source archive'
	@echo '  g2-community-preflight   verify Python, GNU make, Clang, and profile'
	@echo '  g2-community-local-build  test and build the locally hydrated G2 image'

g2-community-preflight:
	$(MAKE) -C g2 community-local-preflight

g2-community-local-build:
	$(MAKE) -C g2 community-local-build
