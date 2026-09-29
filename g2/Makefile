# SPDX-License-Identifier: MIT
# G2 glasses: reference packaging, container analyzers and the Ghidra export
# pipeline for the pseudocode-first workflow (workflow/README.md).
#
# The official s200_v2.2.6.10 payloads are never tracked. Place authorized
# copies where blobs/official/g2-2.2.6.10/PROVENANCE.md says; every target
# checks their identities before use.

PYTHON ?= python3

REFERENCE_MANIFEST ?= manifests/g2-2.2.6.10.json
REFERENCE_BUILD_DIR ?= build/reference
APOLLO_HARVEST_DIR ?= research/corpus/apollo-main/ghidra/decomp
BOOTLOADER_HARVEST_DIR ?= research/corpus/apollo-bootloader/ghidra/decomp
HARVEST_JOBS ?= 8

# Tests for the kept tools: the EVENOTA/container parsers, the EM9305 record
# package, the case, touch and codec analyzers, the Ghidra export pipeline and
# the asset generators. A module skips itself when the official payloads it
# reads are absent.
CORE_TESTS := test_open_cfw test_analyze_g2_codec_fwpk_segments \
	test_analyze_g2_codec_stage2_sections test_analyze_g2_touch_identity \
	test_analyze_em9305_record_package test_em9305_record_package \
	test_analyze_g2_box_function_map test_extract_g2_case_final_decomp \
	test_merge_case_backup test_thumb_branch_audit test_verify_research_corpus \
	test_disassemble_em9305_arcompact test_analyze_apollo_embedded_source_paths \
	test_recover_apollo_embedded_source_paths test_generate_apollo_ghidra_chunks \
	test_run_ghidra_shard_batch test_assetgen_lvgl_font test_assetgen_lvgl_image \
	test_assetgen_nanopb_descriptor test_assetgen_string_pool \
	test_gxdnn_command_emitter test_gxdnn_quantize test_csky_macos_build

.PHONY: all help reference verify reference-verify test core-test research-corpus \
        em9305-record-package ghidra-harvest bootloader-ghidra-harvest \
        csky-toolchain clean

all: test

help:
	@echo 'G2 targets:'
	@echo '  reference              repack the six official payloads into the byte-identical EVENOTA'
	@echo '  verify                 reference + manifest check + research-corpus authentication'
	@echo '  test                   tests for the kept tools (payload-dependent ones skip if absent)'
	@echo '  research-corpus        authenticate research/ against MANIFEST.sha256'
	@echo '  em9305-record-package  rewrite tools/manifests/em9305-record-package-summary.json'
	@echo '  ghidra-harvest         re-export Apollo main pseudocode (OPENCFW_APOLLO_GHIDRA_PROJECT)'
	@echo '  bootloader-ghidra-harvest  same for the Even bootloader (OPENCFW_BOOTLOADER_GHIDRA_PROJECT)'
	@echo '  csky-toolchain         build the pinned C-SKY toolchain for GX8002 analysis (macOS recipe)'
	@echo '  clean                  remove build/'

# Byte-identical repack of the official bundle. It proves the container format
# and payload identities, not source reconstruction.
reference:
	$(PYTHON) tools/open_cfw.py build \
		--manifest "$(REFERENCE_MANIFEST)" \
		--output-dir "$(REFERENCE_BUILD_DIR)"

verify: reference-verify

reference-verify: reference research-corpus
	$(PYTHON) tools/open_cfw.py verify --manifest "$(REFERENCE_MANIFEST)"

test: core-test

core-test:
	@set -e; for t in $(CORE_TESTS); do \
		PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p "$$t.py"; \
	done

research-corpus:
	$(PYTHON) tools/verify_research_corpus.py

em9305-record-package:
	$(PYTHON) tools/analyze_em9305_record_package.py --write-manifest
	@set -e; for t in test_em9305_record_package test_analyze_em9305_record_package; do \
		PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p "$$t.py"; \
	done

# Re-harvest per-function decompilation from an analyzed Ghidra project.
# Needs Ghidra (OPENCFW_GHIDRA_HOME or the harvester's default) and a JDK.
ghidra-harvest:
	$(PYTHON) tools/harvest_ghidra_decomp.py \
		--project "$${OPENCFW_APOLLO_GHIDRA_PROJECT:?set to an analyzed Ghidra project directory}" \
		--program ota_s200_firmware_ota.bin \
		--output "$(APOLLO_HARVEST_DIR)" \
		--jobs "$(HARVEST_JOBS)" \
		$${OPENCFW_GHIDRA_HOME:+--ghidra-home "$$OPENCFW_GHIDRA_HOME"} \
		--expect-executable-sha256 \
		36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863

bootloader-ghidra-harvest:
	$(PYTHON) tools/harvest_ghidra_decomp.py \
		--project "$${OPENCFW_BOOTLOADER_GHIDRA_PROJECT:?set to an analyzed Ghidra project directory}" \
		--project-name apollo_bootloader_template \
		--program ota_s200_bootloader.bin \
		--output "$(BOOTLOADER_HARVEST_DIR)" \
		--jobs "$(HARVEST_JOBS)" \
		$${OPENCFW_GHIDRA_HOME:+--ghidra-home "$$OPENCFW_GHIDRA_HOME"} \
		--expect-executable-sha256 \
		f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5

csky-toolchain:
	$(PYTHON) tools/build_g2_csky_macos.py

clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("build", ignore_errors=True)'
