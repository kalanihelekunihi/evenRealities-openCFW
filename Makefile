PYTHON ?= python3

# Toolchain selection.  openCFW pins compiled overlays byte-for-byte per
# reviewed toolchain profile.  On macOS this resolves to the reviewed Apple
# clang and the canonical `apple-clang` profile; on a host without Apple clang
# (for example Linux with a Homebrew clang) it resolves to a present clang and
# that clang's recorded reproducible profile.  Override either explicitly, e.g.
# `make ring-source OPENCFW_CLANG=/path/clang OPENCFW_TOOLCHAIN_PROFILE=id`.
# The blob-only `reference` build is compiler-independent and stays
# byte-identical under any profile.
OPENCFW_CLANG ?= $(shell for c in /usr/bin/clang /home/linuxbrew/.linuxbrew/opt/llvm/bin/clang clang; do if command -v "$$c" >/dev/null 2>&1; then command -v "$$c"; break; fi; done)
export OPENCFW_CLANG
OPENCFW_TOOLCHAIN_PROFILE ?= $(shell $(PYTHON) tools/detect_toolchain.py --clang "$(OPENCFW_CLANG)" 2>/dev/null || echo apple-clang)
export OPENCFW_TOOLCHAIN_PROFILE

REFERENCE_MANIFEST ?= manifests/g2-2.2.6.10.json
RING_SOURCE_MANIFEST ?= manifests/g2-2.2.6.10-ring-source.json
SOURCE_MANIFEST ?= manifests/g2-2.2.6.10-core-source.json
REFERENCE_BUILD_DIR ?= build/reference
RING_SOURCE_BUILD_DIR ?= build/ring-source
SOURCE_BUILD_DIR ?= build/source
RING_COMPONENT_DIR := components/apollo_main/ring_gesture
RING_COMPONENT_BUILD_DIR := $(RING_COMPONENT_DIR)/build
CORE_COMPONENT_DIR := components/apollo_main/core_overlay
CORE_COMPONENT_BUILD_DIR := $(CORE_COMPONENT_DIR)/build
BOOT_COMPONENT_DIR := components/bootloader/core_overlay
BOOT_COMPONENT_BUILD_DIR := $(BOOT_COMPONENT_DIR)/build
TLSF_DIR := third_party/tlsf
EASYLOGGER_DIR := third_party/easylogger
LITTLEFS_DIR := third_party/littlefs
FREERTOS_DIR := third_party/freertos-kernel
AMBIQSUITE_DIR := third_party/ambiqsuite-apollo510
CMSIS_CORE_DIR := third_party/cmsis-core
CMSIS_FREERTOS_DIR := third_party/cmsis-freertos
LZ4_DIR := third_party/lz4
FREETYPE_DIR := third_party/freetype
FLASHDB_DIR := third_party/flashdb
CMBACKTRACE_DIR := third_party/cmbacktrace
NANOPB_DIR := third_party/nanopb
CORDIO_DIR := third_party/cordio
FREERTOS_PLUS_CLI_DIR := third_party/freertos-plus-cli
LVGL_DIR := third_party/lvgl

.PHONY: all build reference ring-source source component ring-component core-component bootloader-component vendor-snapshots upstream-audits tlsf-snapshot easylogger-snapshot littlefs-snapshot freertos-snapshot ambiqsuite-snapshot cmsis-core-snapshot cmsis-freertos-snapshot lz4-snapshot freetype-snapshot flashdb-snapshot cmbacktrace-snapshot nanopb-snapshot cordio-snapshot freertos-plus-cli-snapshot lvgl-snapshot verify test inspect clean toolchain

all: build

toolchain:
	@echo "OPENCFW_CLANG=$(OPENCFW_CLANG)"
	@echo "OPENCFW_TOOLCHAIN_PROFILE=$(OPENCFW_TOOLCHAIN_PROFILE)"

build: reference ring-source source

ring-component:
	$(PYTHON) $(RING_COMPONENT_DIR)/build_component.py

tlsf-snapshot:
	$(PYTHON) $(TLSF_DIR)/verify_snapshot.py

easylogger-snapshot:
	$(PYTHON) $(EASYLOGGER_DIR)/verify_snapshot.py

littlefs-snapshot:
	$(PYTHON) $(LITTLEFS_DIR)/verify_snapshot.py

freertos-snapshot:
	$(PYTHON) $(FREERTOS_DIR)/verify_snapshot.py

ambiqsuite-snapshot:
	$(PYTHON) $(AMBIQSUITE_DIR)/verify_snapshot.py

cmsis-core-snapshot:
	$(PYTHON) $(CMSIS_CORE_DIR)/verify_snapshot.py

cmsis-freertos-snapshot:
	$(PYTHON) $(CMSIS_FREERTOS_DIR)/verify_snapshot.py

lz4-snapshot:
	$(PYTHON) $(LZ4_DIR)/verify_snapshot.py

freetype-snapshot:
	$(PYTHON) $(FREETYPE_DIR)/verify_snapshot.py

flashdb-snapshot:
	$(PYTHON) $(FLASHDB_DIR)/verify_snapshot.py

cmbacktrace-snapshot:
	$(PYTHON) $(CMBACKTRACE_DIR)/verify_snapshot.py

nanopb-snapshot:
	$(PYTHON) $(NANOPB_DIR)/verify_snapshot.py

cordio-snapshot:
	$(PYTHON) $(CORDIO_DIR)/verify_snapshot.py

freertos-plus-cli-snapshot:
	$(PYTHON) $(FREERTOS_PLUS_CLI_DIR)/verify_snapshot.py

lvgl-snapshot:
	$(PYTHON) $(LVGL_DIR)/verify_snapshot.py

vendor-snapshots: tlsf-snapshot easylogger-snapshot littlefs-snapshot freertos-snapshot ambiqsuite-snapshot cmsis-core-snapshot cmsis-freertos-snapshot lz4-snapshot freetype-snapshot flashdb-snapshot cmbacktrace-snapshot nanopb-snapshot cordio-snapshot freertos-plus-cli-snapshot lvgl-snapshot

upstream-audits:
	$(PYTHON) tools/analyze_g2_littlefs_ports.py
	$(PYTHON) tools/analyze_g2_littlefs_mspi_transport.py
	$(PYTHON) tools/analyze_g2_mspi_interrupt_clear.py
	$(PYTHON) tools/analyze_g2_freertos_port.py
	$(PYTHON) tools/analyze_g2_freertos_assert_port_seam.py
	$(PYTHON) tools/analyze_g2_freertos_ntz_context_handlers.py
	$(PYTHON) tools/analyze_g2_flashdb.py
	$(PYTHON) tools/analyze_g2_cmbacktrace_version.py
	$(PYTHON) tools/analyze_g2_nanopb_point_release.py
	$(PYTHON) tools/analyze_g2_cordio_version.py
	$(PYTHON) tools/analyze_g2_freertos_plus_cli.py
	$(PYTHON) tools/analyze_g2_lvgl_version.py
	$(PYTHON) tools/analyze_g2_tinyframe_send_version.py

core-component: vendor-snapshots
	$(PYTHON) $(CORE_COMPONENT_DIR)/build_component.py

bootloader-component: littlefs-snapshot
	$(PYTHON) $(BOOT_COMPONENT_DIR)/build_component.py

component: bootloader-component core-component

reference:
	$(PYTHON) tools/open_cfw.py build \
		--manifest "$(REFERENCE_MANIFEST)" \
		--output-dir "$(REFERENCE_BUILD_DIR)"

ring-source: ring-component
	$(PYTHON) tools/open_cfw.py build \
		--manifest "$(RING_SOURCE_MANIFEST)" \
		--output-dir "$(RING_SOURCE_BUILD_DIR)"

source: bootloader-component core-component
	$(PYTHON) tools/open_cfw.py build \
		--manifest "$(SOURCE_MANIFEST)" \
		--output-dir "$(SOURCE_BUILD_DIR)"

verify: ring-component bootloader-component core-component upstream-audits
	$(PYTHON) tools/open_cfw.py verify --manifest "$(REFERENCE_MANIFEST)"
	$(PYTHON) tools/open_cfw.py verify --manifest "$(RING_SOURCE_MANIFEST)"
	$(PYTHON) tools/open_cfw.py verify --manifest "$(SOURCE_MANIFEST)"

test: ring-component bootloader-component core-component
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v

inspect: source
	$(PYTHON) -m json.tool "$(SOURCE_BUILD_DIR)/flash-plan.json"

clean:
	$(PYTHON) -c 'from pathlib import Path; import shutil; root=Path.cwd().resolve(); targets=tuple((root/path).resolve() for path in ("build", "$(RING_COMPONENT_BUILD_DIR)", "$(CORE_COMPONENT_BUILD_DIR)", "$(BOOT_COMPONENT_BUILD_DIR)")); assert all(root in path.parents and path != root for path in targets); [shutil.rmtree(path, ignore_errors=True) for path in targets]'
