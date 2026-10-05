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
RESOURCE_PAYLOAD ?= blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin
RESOURCE_DIR ?= build/resources/l8
RESOURCE_REPACK ?= build/resources/repacked-apollo-main.bin
FOUNDATION_CC ?= clang
FOUNDATION_CFLAGS ?= --target=arm-none-eabi -mcpu=cortex-m0plus -mthumb -ffreestanding -fno-builtin -std=c11 -Wall -Wextra -Werror
FOUNDATION_OBJECT ?= build/foundation/touch_scb.o
SCB_SIM_DIR ?= build/foundation/touch-scb-simulator
SCB_SIM_PYTHON ?= $(PYTHON)
SCB_SIM_LD ?= arm-none-eabi-ld
SCB_SIM_REPORT ?= $(SCB_SIM_DIR)/comparison.json
AMBIQ_SIM_DIR ?= build/foundation/ambiq-mspi-simulator
AMBIQ_SIM_REPORT ?= $(AMBIQ_SIM_DIR)/comparison.json
AMBIQ_LIFECYCLE_REPORT ?= $(AMBIQ_SIM_DIR)/lifecycle-comparison.json
AMBIQ_SIM_CFLAGS ?= --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -Wall -Wextra -Werror -O2

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
	test_gxdnn_command_emitter test_gxdnn_quantize test_csky_macos_build \
	test_preserve_l8_resources test_touch_scb test_touch_scb_mmio test_touch_scb_simulator test_touch_scb_tx test_touch_scb_fifo test_ambiq_mspi test_ambiq_mspi_lifecycle test_ambiq_mspi_cmdq test_ambiq_gpio test_radio_gpio test_wsf_radio test_freertos_event_group test_freertos_queue test_freertos_daemon test_freertos_ready test_freertos_resume test_freertos_tick test_ambiq_gpio_config test_wsf_timer_stop

.PHONY: all help reference verify reference-verify test core-test research-corpus \
        em9305-record-package ghidra-harvest bootloader-ghidra-harvest \
        csky-toolchain resource-export resource-verify resource-repack foundation-test foundation-object touch-scb-simulator touch-scb-simulator-test ambiq-mspi-simulator ambiq-mspi-simulator-test clean

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
	@echo '  resource-export/verify/repack  optional local, hash-pinned lossless L8 resource preservation'
	@echo '  foundation-test        C touch-wrapper and resource preservation tests'
	@echo '  foundation-object      compile reusable touch wrapper for Cortex-M0+ (not firmware-linked)'
	@echo '  touch-scb-simulator/test  link source-defined ARM module and compare execution with original FIFO code'
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

foundation-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_touch_scb*.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_ambiq*.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_preserve_l8_resources.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_radio_gpio.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_wsf_radio.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_event_group.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_queue.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_daemon.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_ready.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_resume.py'
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -t . -p 'test_freertos_tick.py'

foundation-object: $(FOUNDATION_OBJECT)

$(FOUNDATION_OBJECT): components/foundation/touch_scb/touch_scb.c components/foundation/touch_scb/touch_scb.h
	mkdir -p "$(@D)"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -I components/foundation/touch_scb -c "$<" -o "$@"

SCB_SIM_SOURCES := components/foundation/touch_scb/touch_scb.c components/foundation/touch_scb/touch_scb_mmio.c components/foundation/touch_scb/touch_scb_tx.c components/foundation/touch_scb/touch_scb_fifo.c components/foundation/touch_scb/simulator/entry.c
SCB_SIM_HEADERS := components/foundation/touch_scb/touch_scb.h components/foundation/touch_scb/touch_scb_mmio.h components/foundation/touch_scb/touch_scb_tx.h components/foundation/touch_scb/touch_scb_fifo.h
SCB_SIM_OBJECTS := $(SCB_SIM_DIR)/touch_scb.o $(SCB_SIM_DIR)/touch_scb_mmio.o $(SCB_SIM_DIR)/touch_scb_tx.o $(SCB_SIM_DIR)/touch_scb_fifo.o $(SCB_SIM_DIR)/entry.o

touch-scb-simulator: $(SCB_SIM_DIR)/touch_scb.elf

$(SCB_SIM_DIR)/touch_scb.elf: $(SCB_SIM_SOURCES) $(SCB_SIM_HEADERS) components/foundation/touch_scb/simulator/module.ld
	mkdir -p "$(SCB_SIM_DIR)"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -O2 -ffunction-sections -fdata-sections -c components/foundation/touch_scb/touch_scb.c -o "$(SCB_SIM_DIR)/touch_scb.o"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -O2 -ffunction-sections -fdata-sections -c components/foundation/touch_scb/touch_scb_mmio.c -o "$(SCB_SIM_DIR)/touch_scb_mmio.o"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -O2 -ffunction-sections -fdata-sections -c components/foundation/touch_scb/touch_scb_tx.c -o "$(SCB_SIM_DIR)/touch_scb_tx.o"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -O2 -ffunction-sections -fdata-sections -c components/foundation/touch_scb/touch_scb_fifo.c -o "$(SCB_SIM_DIR)/touch_scb_fifo.o"
	$(FOUNDATION_CC) $(FOUNDATION_CFLAGS) -O2 -ffunction-sections -fdata-sections -c components/foundation/touch_scb/simulator/entry.c -o "$(SCB_SIM_DIR)/entry.o"
	$(SCB_SIM_LD) -T components/foundation/touch_scb/simulator/module.ld -Map "$(SCB_SIM_DIR)/touch_scb.map" -o "$@" $(SCB_SIM_OBJECTS)

touch-scb-simulator-test: touch-scb-simulator
	$(SCB_SIM_PYTHON) components/foundation/touch_scb/simulator/verify.py --elf "$(SCB_SIM_DIR)/touch_scb.elf" --output "$(SCB_SIM_REPORT)"

resource-export:
	$(PYTHON) tools/preserve_l8_resources.py export --payload "$(RESOURCE_PAYLOAD)" --output-dir "$(RESOURCE_DIR)"

resource-verify:
	$(PYTHON) tools/preserve_l8_resources.py verify --resources "$(RESOURCE_DIR)"

resource-repack:
	$(PYTHON) tools/preserve_l8_resources.py repack --payload "$(RESOURCE_PAYLOAD)" --resources "$(RESOURCE_DIR)" --output "$(RESOURCE_REPACK)"

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

# Source-only Apollo HAL subset: callable simulator, no production provider.
AMBIQ_COMPONENT := components/foundation/ambiq_mspi
AMBIQ_SIM_INPUTS := $(AMBIQ_COMPONENT)/ambiq_mspi_interrupts.c $(AMBIQ_COMPONENT)/ambiq_mspi_lifecycle.c $(AMBIQ_COMPONENT)/simulator/lifecycle_seams.c $(AMBIQ_COMPONENT)/ambiq_mspi_interrupts.h $(AMBIQ_COMPONENT)/ambiq_mspi_compat.h $(AMBIQ_COMPONENT)/simulator/entry.c $(AMBIQ_COMPONENT)/simulator/module.ld
ambiq-mspi-simulator: $(AMBIQ_SIM_DIR)/ambiq_mspi.elf

$(AMBIQ_SIM_DIR)/ambiq_mspi.elf: $(AMBIQ_SIM_INPUTS)
	mkdir -p "$(AMBIQ_SIM_DIR)"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/ambiq_mspi_interrupts.c -o "$(AMBIQ_SIM_DIR)/interrupts.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/ambiq_mspi_lifecycle.c -o "$(AMBIQ_SIM_DIR)/lifecycle.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/simulator/lifecycle_seams.c -o "$(AMBIQ_SIM_DIR)/lifecycle_seams.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/simulator/entry.c -o "$(AMBIQ_SIM_DIR)/entry.o"
	$(SCB_SIM_LD) -T $(AMBIQ_COMPONENT)/simulator/module.ld -Map "$(AMBIQ_SIM_DIR)/ambiq_mspi.map" -o "$@" "$(AMBIQ_SIM_DIR)/interrupts.o" "$(AMBIQ_SIM_DIR)/lifecycle.o" "$(AMBIQ_SIM_DIR)/lifecycle_seams.o" "$(AMBIQ_SIM_DIR)/entry.o"

ambiq-mspi-simulator-test: ambiq-mspi-simulator
	$(SCB_SIM_PYTHON) $(AMBIQ_COMPONENT)/simulator/verify.py --elf "$(AMBIQ_SIM_DIR)/ambiq_mspi.elf" --output "$(AMBIQ_SIM_REPORT)"

.PHONY: ambiq-mspi-lifecycle-test
ambiq-mspi-lifecycle-test: ambiq-mspi-simulator
	$(SCB_SIM_PYTHON) $(AMBIQ_COMPONENT)/simulator/verify_lifecycle.py --elf "$(AMBIQ_SIM_DIR)/ambiq_mspi.elf" --output "$(AMBIQ_LIFECYCLE_REPORT)"

# Real stock CMDQ disable/forced-term subset; delay and critical-enter synthetic.
AMBIQ_CQ_DIR ?= build/foundation/ambiq-cmdq-simulator
AMBIQ_CQ_CRITICAL_FLAGS ?=
.PHONY: ambiq-cmdq-simulator
ambiq-cmdq-simulator: $(AMBIQ_CQ_DIR)/ambiq_mspi.elf
$(AMBIQ_CQ_DIR)/ambiq_mspi.elf: $(AMBIQ_SIM_INPUTS) $(AMBIQ_COMPONENT)/ambiq_cmdq.c $(AMBIQ_COMPONENT)/ambiq_cmdq.h $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.h $(AMBIQ_CQ_DIR)/profile.txt ambiq-cq-profile-force
	mkdir -p "$(AMBIQ_CQ_DIR)"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/ambiq_mspi_interrupts.c -o "$(AMBIQ_CQ_DIR)/interrupts.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/ambiq_mspi_lifecycle.c -o "$(AMBIQ_CQ_DIR)/lifecycle.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -DOPENCFW_REAL_CMDQ $(AMBIQ_CQ_CRITICAL_FLAGS) -c $(AMBIQ_COMPONENT)/simulator/lifecycle_seams.c -o "$(AMBIQ_CQ_DIR)/seams.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) $(AMBIQ_CQ_CRITICAL_FLAGS) -c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c -o "$(AMBIQ_CQ_DIR)/critical.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/ambiq_cmdq.c -o "$(AMBIQ_CQ_DIR)/cmdq.o"
	$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) -c $(AMBIQ_COMPONENT)/simulator/entry.c -o "$(AMBIQ_CQ_DIR)/entry.o"
	$(SCB_SIM_LD) -T $(AMBIQ_COMPONENT)/simulator/module.ld -o "$@" "$(AMBIQ_CQ_DIR)/interrupts.o" "$(AMBIQ_CQ_DIR)/lifecycle.o" "$(AMBIQ_CQ_DIR)/seams.o" "$(AMBIQ_CQ_DIR)/cmdq.o" "$(AMBIQ_CQ_DIR)/critical.o" "$(AMBIQ_CQ_DIR)/entry.o"

AMBIQ_CQ_REPORT ?= $(AMBIQ_CQ_DIR)/comparison.json
.PHONY: ambiq-cmdq-simulator-test
ambiq-cmdq-simulator-test: ambiq-cmdq-simulator
	$(SCB_SIM_PYTHON) $(AMBIQ_COMPONENT)/simulator/verify_cmdq.py --elf "$(AMBIQ_CQ_DIR)/ambiq_mspi.elf" --output "$(AMBIQ_CQ_REPORT)"

AMBIQ_CRITICAL_DIR ?= build/foundation/ambiq-critical-simulator
.PHONY: ambiq-critical-simulator
ambiq-critical-simulator:
	$(MAKE) ambiq-cmdq-simulator AMBIQ_CQ_DIR="$(AMBIQ_CRITICAL_DIR)" AMBIQ_CQ_CRITICAL_FLAGS=-DOPENCFW_REAL_CRITICAL

# Profile flags are build inputs, including when a caller reuses an output dir.
.PHONY: ambiq-cq-profile-force
ambiq-cq-profile-force:
$(AMBIQ_CQ_DIR)/profile.txt: ambiq-cq-profile-force
	mkdir -p "$(AMBIQ_CQ_DIR)"
	$(PYTHON) -c 'import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=sys.argv[2]+"\n"; p.write_text(s) if not p.exists() or p.read_text()!=s else None' "$@" "$(FOUNDATION_CC) $(AMBIQ_SIM_CFLAGS) $(AMBIQ_CQ_CRITICAL_FLAGS)"

# Separate source-only GPIO IRQ family with real PRIMASK entry/restore.
GPIO_COMPONENT := components/foundation/ambiq_gpio
GPIO_SIM_DIR ?= build/foundation/ambiq-gpio-simulator
GPIO_SIM_CFLAGS ?= --target=arm-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -ffreestanding -fno-builtin -std=c11 -Wall -Wextra -Werror -O2 -fwrapv
.PHONY: ambiq-gpio-simulator ambiq-gpio-force
ambiq-gpio-force:
ambiq-gpio-simulator: $(GPIO_SIM_DIR)/ambiq_gpio.elf
$(GPIO_SIM_DIR)/ambiq_gpio.elf: $(GPIO_COMPONENT)/ambiq_gpio_irq.c $(GPIO_COMPONENT)/ambiq_gpio.h $(GPIO_COMPONENT)/ambiq_gpio_compat.h $(GPIO_COMPONENT)/simulator/module.ld $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.h ambiq-gpio-force
	mkdir -p "$(GPIO_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_COMPONENT)/ambiq_gpio_irq.c -o "$(GPIO_SIM_DIR)/gpio.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -DOPENCFW_REAL_CRITICAL -c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c -o "$(GPIO_SIM_DIR)/critical.o"
	$(SCB_SIM_LD) -T $(GPIO_COMPONENT)/simulator/module.ld -o "$@" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"

GPIO_SIM_REPORT ?= $(GPIO_SIM_DIR)/comparison.json
.PHONY: ambiq-gpio-simulator-test
ambiq-gpio-simulator-test: ambiq-gpio-simulator
	$(SCB_SIM_PYTHON) $(GPIO_COMPONENT)/simulator/verify.py --elf "$(GPIO_SIM_DIR)/ambiq_gpio.elf" --output "$(GPIO_SIM_REPORT)"

# Bounded reconstructed radio GPIO consumer; scheduler remains a fixture boundary.
RADIO_GPIO_COMPONENT := components/foundation/radio_gpio
RADIO_GPIO_SIM_DIR ?= build/foundation/radio-gpio-simulator
.PHONY: radio-gpio-simulator
radio-gpio-simulator: ambiq-gpio-simulator
	mkdir -p "$(RADIO_GPIO_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(RADIO_GPIO_COMPONENT)/radio_gpio.c -o "$(RADIO_GPIO_SIM_DIR)/radio.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(RADIO_GPIO_COMPONENT)/simulator/scheduler_boundary.c -o "$(RADIO_GPIO_SIM_DIR)/scheduler.o"
	$(SCB_SIM_LD) -T $(RADIO_GPIO_COMPONENT)/simulator/module.ld -o "$(RADIO_GPIO_SIM_DIR)/radio_gpio.elf" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(RADIO_GPIO_SIM_DIR)/scheduler.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"

RADIO_GPIO_SIM_REPORT ?= $(RADIO_GPIO_SIM_DIR)/comparison.json
.PHONY: radio-gpio-simulator-test
radio-gpio-simulator-test: radio-gpio-simulator
	$(SCB_SIM_PYTHON) $(RADIO_GPIO_COMPONENT)/simulator/verify.py --elf "$(RADIO_GPIO_SIM_DIR)/radio_gpio.elf" --output "$(RADIO_GPIO_SIM_REPORT)"

WSF_COMPONENT := components/foundation/wsf_radio
WSF_SIM_DIR ?= build/foundation/wsf-radio-simulator
.PHONY: wsf-radio-simulator
wsf-radio-simulator: radio-gpio-simulator
	mkdir -p "$(WSF_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(WSF_COMPONENT)/wsf_radio.c -o "$(WSF_SIM_DIR)/wsf.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(WSF_COMPONENT)/simulator/providers.c -o "$(WSF_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(WSF_COMPONENT)/simulator/module.ld -o "$(WSF_SIM_DIR)/wsf_radio.elf" "$(WSF_SIM_DIR)/wsf.o" "$(WSF_SIM_DIR)/providers.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"

WSF_SIM_REPORT ?= $(WSF_SIM_DIR)/comparison.json
.PHONY: wsf-radio-simulator-test
wsf-radio-simulator-test: wsf-radio-simulator
	$(SCB_SIM_PYTHON) $(WSF_COMPONENT)/simulator/verify.py --elf "$(WSF_SIM_DIR)/wsf_radio.elf" --output "$(WSF_SIM_REPORT)"

EVENT_GROUP_COMPONENT := components/foundation/freertos_event_group
EVENT_GROUP_SIM_DIR ?= build/foundation/event-group-wsf-simulator
.PHONY: event-group-wsf-simulator
event-group-wsf-simulator: wsf-radio-simulator
	mkdir -p "$(EVENT_GROUP_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(EVENT_GROUP_COMPONENT)/event_groups_subset.c -o "$(EVENT_GROUP_SIM_DIR)/event.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(EVENT_GROUP_COMPONENT)/timer_pend_subset.c -o "$(EVENT_GROUP_SIM_DIR)/pend.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(EVENT_GROUP_COMPONENT)/wsf_event_adapter.c -o "$(EVENT_GROUP_SIM_DIR)/adapter.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(EVENT_GROUP_COMPONENT)/simulator/providers.c -o "$(EVENT_GROUP_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(EVENT_GROUP_SIM_DIR)/event_group_wsf.elf" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(EVENT_GROUP_SIM_DIR)/providers.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"

EVENT_GROUP_SIM_REPORT ?= $(EVENT_GROUP_SIM_DIR)/comparison.json
.PHONY: event-group-wsf-simulator-test
event-group-wsf-simulator-test: event-group-wsf-simulator
	$(SCB_SIM_PYTHON) $(EVENT_GROUP_COMPONENT)/simulator/verify.py --elf "$(EVENT_GROUP_SIM_DIR)/event_group_wsf.elf" --output "$(EVENT_GROUP_SIM_REPORT)"

QUEUE_COMPONENT := components/foundation/freertos_queue
QUEUE_SIM_DIR ?= build/foundation/timer-queue-wsf-simulator
.PHONY: timer-queue-wsf-simulator
timer-queue-wsf-simulator: event-group-wsf-simulator
	mkdir -p "$(QUEUE_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(QUEUE_COMPONENT)/queue_subset.c -o "$(QUEUE_SIM_DIR)/queue.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(QUEUE_COMPONENT)/queue_adapter.c -o "$(QUEUE_SIM_DIR)/adapter.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(QUEUE_COMPONENT)/simulator/providers.c -o "$(QUEUE_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(QUEUE_SIM_DIR)/timer_queue_wsf.elf" "$(QUEUE_SIM_DIR)/queue.o" "$(QUEUE_SIM_DIR)/adapter.o" "$(QUEUE_SIM_DIR)/providers.o" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"
QUEUE_SIM_REPORT ?= $(QUEUE_SIM_DIR)/comparison.json
.PHONY: timer-queue-wsf-simulator-test
timer-queue-wsf-simulator-test: timer-queue-wsf-simulator
	$(SCB_SIM_PYTHON) $(QUEUE_COMPONENT)/simulator/verify.py --elf "$(QUEUE_SIM_DIR)/timer_queue_wsf.elf" --output "$(QUEUE_SIM_REPORT)"

DAEMON_COMPONENT := components/foundation/freertos_daemon
DAEMON_SIM_DIR ?= build/foundation/timer-daemon-wsf-simulator
.PHONY: timer-daemon-wsf-simulator
timer-daemon-wsf-simulator: timer-queue-wsf-simulator
	mkdir -p "$(DAEMON_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(DAEMON_COMPONENT)/daemon.c -o "$(DAEMON_SIM_DIR)/daemon.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(DAEMON_COMPONENT)/receive_copy.c -o "$(DAEMON_SIM_DIR)/copy.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(DAEMON_COMPONENT)/task_critical.c -o "$(DAEMON_SIM_DIR)/taskcritical.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(DAEMON_COMPONENT)/simulator/providers.c -o "$(DAEMON_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(DAEMON_SIM_DIR)/timer_daemon_wsf.elf" "$(DAEMON_SIM_DIR)/daemon.o" "$(DAEMON_SIM_DIR)/copy.o" "$(DAEMON_SIM_DIR)/taskcritical.o" "$(DAEMON_SIM_DIR)/providers.o" "$(QUEUE_SIM_DIR)/queue.o" "$(QUEUE_SIM_DIR)/adapter.o" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"
DAEMON_SIM_REPORT ?= $(DAEMON_SIM_DIR)/comparison.json
.PHONY: timer-daemon-wsf-simulator-test
timer-daemon-wsf-simulator-test: timer-daemon-wsf-simulator
	$(SCB_SIM_PYTHON) $(DAEMON_COMPONENT)/simulator/verify.py --elf "$(DAEMON_SIM_DIR)/timer_daemon_wsf.elf" --output "$(DAEMON_SIM_REPORT)"

READY_COMPONENT := components/foundation/freertos_ready
READY_SIM_DIR ?= build/foundation/rtos-ready-wsf-simulator
.PHONY: rtos-ready-wsf-simulator
rtos-ready-wsf-simulator: timer-daemon-wsf-simulator
	mkdir -p "$(READY_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(READY_COMPONENT)/tasks_subset.c -o "$(READY_SIM_DIR)/tasks.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(READY_COMPONENT)/list_subset.c -o "$(READY_SIM_DIR)/list.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(READY_COMPONENT)/ready_adapter.c -o "$(READY_SIM_DIR)/adapter.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(READY_COMPONENT)/simulator/providers.c -o "$(READY_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(READY_SIM_DIR)/rtos_ready_wsf.elf" "$(READY_SIM_DIR)/tasks.o" "$(READY_SIM_DIR)/list.o" "$(READY_SIM_DIR)/adapter.o" "$(READY_SIM_DIR)/providers.o" "$(DAEMON_SIM_DIR)/daemon.o" "$(DAEMON_SIM_DIR)/copy.o" "$(DAEMON_SIM_DIR)/taskcritical.o" "$(QUEUE_SIM_DIR)/queue.o" "$(QUEUE_SIM_DIR)/adapter.o" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"
READY_SIM_REPORT ?= $(READY_SIM_DIR)/comparison.json
.PHONY: rtos-ready-wsf-simulator-test
rtos-ready-wsf-simulator-test: rtos-ready-wsf-simulator
	$(SCB_SIM_PYTHON) $(READY_COMPONENT)/simulator/verify.py --elf "$(READY_SIM_DIR)/rtos_ready_wsf.elf" --output "$(READY_SIM_REPORT)"

RESUME_COMPONENT := components/foundation/freertos_resume
RESUME_SIM_DIR ?= build/foundation/rtos-resume-wsf-simulator
.PHONY: rtos-resume-wsf-simulator
rtos-resume-wsf-simulator: rtos-ready-wsf-simulator
	mkdir -p "$(RESUME_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(RESUME_COMPONENT)/tasks_resume.c -o "$(RESUME_SIM_DIR)/resume.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(RESUME_COMPONENT)/yield_request.c -o "$(RESUME_SIM_DIR)/yield.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(RESUME_COMPONENT)/simulator/providers.c -o "$(RESUME_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(RESUME_SIM_DIR)/rtos_resume_wsf.elf" "$(RESUME_SIM_DIR)/resume.o" "$(RESUME_SIM_DIR)/yield.o" "$(READY_SIM_DIR)/tasks.o" "$(READY_SIM_DIR)/list.o" "$(READY_SIM_DIR)/adapter.o" "$(RESUME_SIM_DIR)/providers.o" "$(DAEMON_SIM_DIR)/daemon.o" "$(DAEMON_SIM_DIR)/copy.o" "$(DAEMON_SIM_DIR)/taskcritical.o" "$(QUEUE_SIM_DIR)/queue.o" "$(QUEUE_SIM_DIR)/adapter.o" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"
RESUME_SIM_REPORT ?= $(RESUME_SIM_DIR)/comparison.json
.PHONY: rtos-resume-wsf-simulator-test
rtos-resume-wsf-simulator-test: rtos-resume-wsf-simulator
	$(SCB_SIM_PYTHON) $(RESUME_COMPONENT)/simulator/verify.py --elf "$(RESUME_SIM_DIR)/rtos_resume_wsf.elf" --output "$(RESUME_SIM_REPORT)"

TICK_COMPONENT := components/foundation/freertos_tick
TICK_SIM_CFLAGS ?= $(GPIO_SIM_CFLAGS) -O0
TICK_SIM_DIR ?= build/foundation/rtos-tick-wsf-simulator
.PHONY: rtos-tick-wsf-simulator
rtos-tick-wsf-simulator: rtos-resume-wsf-simulator
	mkdir -p "$(TICK_SIM_DIR)"
	$(FOUNDATION_CC) $(TICK_SIM_CFLAGS) -c $(TICK_COMPONENT)/tasks_tick.c -o "$(TICK_SIM_DIR)/tick.o"
	$(FOUNDATION_CC) $(TICK_SIM_CFLAGS) -c $(RESUME_COMPONENT)/tasks_resume.c -o "$(TICK_SIM_DIR)/resume.o"
	$(FOUNDATION_CC) $(TICK_SIM_CFLAGS) -c $(READY_COMPONENT)/list_subset.c -o "$(TICK_SIM_DIR)/list.o"
	$(FOUNDATION_CC) $(TICK_SIM_CFLAGS) -c $(TICK_COMPONENT)/simulator/providers.c -o "$(TICK_SIM_DIR)/providers.o"
	$(SCB_SIM_LD) -T $(EVENT_GROUP_COMPONENT)/simulator/module.ld -o "$(TICK_SIM_DIR)/rtos_tick_wsf.elf" "$(TICK_SIM_DIR)/tick.o" "$(TICK_SIM_DIR)/resume.o" "$(RESUME_SIM_DIR)/yield.o" "$(READY_SIM_DIR)/tasks.o" "$(TICK_SIM_DIR)/list.o" "$(READY_SIM_DIR)/adapter.o" "$(TICK_SIM_DIR)/providers.o" "$(DAEMON_SIM_DIR)/daemon.o" "$(DAEMON_SIM_DIR)/copy.o" "$(DAEMON_SIM_DIR)/taskcritical.o" "$(QUEUE_SIM_DIR)/queue.o" "$(QUEUE_SIM_DIR)/adapter.o" "$(EVENT_GROUP_SIM_DIR)/event.o" "$(EVENT_GROUP_SIM_DIR)/pend.o" "$(EVENT_GROUP_SIM_DIR)/adapter.o" "$(WSF_SIM_DIR)/wsf.o" "$(RADIO_GPIO_SIM_DIR)/radio.o" "$(GPIO_SIM_DIR)/gpio.o" "$(GPIO_SIM_DIR)/critical.o"
TICK_SIM_REPORT ?= $(TICK_SIM_DIR)/comparison.json
.PHONY: rtos-tick-wsf-simulator-test
rtos-tick-wsf-simulator-test: rtos-tick-wsf-simulator
	$(SCB_SIM_PYTHON) $(TICK_COMPONENT)/simulator/verify.py --elf "$(TICK_SIM_DIR)/rtos_tick_wsf.elf" --output "$(TICK_SIM_REPORT)"

# Pinned board GPIO pad configuration; independent of scheduler simulation.
GPIO_CONFIG_COMPONENT := components/foundation/ambiq_gpio_config
GPIO_CONFIG_SIM_DIR ?= build/foundation/radio-timer-stop-simulator
GPIO_CONFIG_SIM_REPORT ?= $(GPIO_CONFIG_SIM_DIR)/comparison.json
GPIO_CONTROL_SIM_REPORT ?= $(GPIO_CONFIG_SIM_DIR)/control-comparison.json
GPIO_TIMER_SIM_REPORT ?= $(GPIO_CONFIG_SIM_DIR)/timer-comparison.json
.PHONY: ambiq-gpio-config-simulator ambiq-gpio-config-simulator-test
ambiq-gpio-config-simulator:
	mkdir -p "$(GPIO_CONFIG_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/ambiq_gpio_config.c -o "$(GPIO_CONFIG_SIM_DIR)/config.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -DOPENCFW_REAL_CRITICAL -c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c -o "$(GPIO_CONFIG_SIM_DIR)/critical.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/gpio_state.c -o "$(GPIO_CONFIG_SIM_DIR)/state.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/radio_board.c -o "$(GPIO_CONFIG_SIM_DIR)/board.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/gpio_interrupt_control.c -o "$(GPIO_CONFIG_SIM_DIR)/control.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/radio_control.c -o "$(GPIO_CONFIG_SIM_DIR)/radio_control.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c components/foundation/wsf_timer/wsf_timer_stop.c -o "$(GPIO_CONFIG_SIM_DIR)/timer.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -ffunction-sections -fdata-sections -c components/foundation/wsf_radio/wsf_radio.c -o "$(GPIO_CONFIG_SIM_DIR)/wsf_port.o"
	$(SCB_SIM_LD) --gc-sections --undefined=opencfw_radio_timer_gpio_shutdown_phase -T $(GPIO_CONFIG_COMPONENT)/simulator/module.ld -o "$(GPIO_CONFIG_SIM_DIR)/gpio_config.elf" "$(GPIO_CONFIG_SIM_DIR)/config.o" "$(GPIO_CONFIG_SIM_DIR)/state.o" "$(GPIO_CONFIG_SIM_DIR)/board.o" "$(GPIO_CONFIG_SIM_DIR)/control.o" "$(GPIO_CONFIG_SIM_DIR)/radio_control.o" "$(GPIO_CONFIG_SIM_DIR)/timer.o" "$(GPIO_CONFIG_SIM_DIR)/wsf_port.o" "$(GPIO_CONFIG_SIM_DIR)/critical.o"
ambiq-gpio-config-simulator-test: ambiq-gpio-config-simulator
	$(SCB_SIM_PYTHON) $(GPIO_CONFIG_COMPONENT)/simulator/verify.py --elf "$(GPIO_CONFIG_SIM_DIR)/gpio_config.elf" --output "$(GPIO_CONFIG_SIM_REPORT)"
	$(SCB_SIM_PYTHON) $(GPIO_CONFIG_COMPONENT)/simulator/verify_control.py --elf "$(GPIO_CONFIG_SIM_DIR)/gpio_config.elf" --output "$(GPIO_CONTROL_SIM_REPORT)"
	$(SCB_SIM_PYTHON) components/foundation/wsf_timer/verify.py --elf "$(GPIO_CONFIG_SIM_DIR)/gpio_config.elf" --output "$(GPIO_TIMER_SIM_REPORT)"

# Reconstructed transport pad dispatcher with real pinned GPIO/PRIMASK providers.
TRANSPORT_PADS_SIM_DIR ?= build/foundation/radio-transport-pads-simulator
.PHONY: radio-transport-pads-simulator
radio-transport-pads-simulator:
	mkdir -p "$(TRANSPORT_PADS_SIM_DIR)"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c components/foundation/radio_transport_pads/transport_pads.c -o "$(TRANSPORT_PADS_SIM_DIR)/pads.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -c $(GPIO_CONFIG_COMPONENT)/ambiq_gpio_config.c -o "$(TRANSPORT_PADS_SIM_DIR)/config.o"
	$(FOUNDATION_CC) $(GPIO_SIM_CFLAGS) -DOPENCFW_REAL_CRITICAL -c $(AMBIQ_COMPONENT)/ambiq_interrupt_mask.c -o "$(TRANSPORT_PADS_SIM_DIR)/critical.o"
	$(SCB_SIM_LD) -T $(GPIO_CONFIG_COMPONENT)/simulator/module.ld -o "$(TRANSPORT_PADS_SIM_DIR)/transport_pads.elf" "$(TRANSPORT_PADS_SIM_DIR)/pads.o" "$(TRANSPORT_PADS_SIM_DIR)/config.o" "$(TRANSPORT_PADS_SIM_DIR)/critical.o"
