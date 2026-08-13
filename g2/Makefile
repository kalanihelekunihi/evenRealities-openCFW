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
RING_BUFFER_DIR := third_party/ring-buffer
TINYFRAME_DIR := third_party/tinyframe
CJSON_DIR := third_party/cJSON
AMBIQSUITE_ANCC_DIR := third_party/ambiqsuite-ancc-profile
AMBIQSUITE_AMOTA_DIR := third_party/ambiqsuite-amota-profile
AMBIQSUITE_CORDIO_APP_DIR := third_party/ambiqsuite-cordio-app-framework

.PHONY: all build reference ring-source source component ring-component core-component bootloader-component vendor-snapshots upstream-audits tlsf-snapshot easylogger-snapshot littlefs-snapshot freertos-snapshot freertos-g2-tcb-patch freertos-queue-receive-from-isr ambiqsuite-snapshot ambiqsuite-ancc-snapshot ambiqsuite-ancc-profile-closure cmsis-core-snapshot cmsis-freertos-snapshot cmsis-freertos-linked-census cmsis-freertos-core-leaves cmsis-freertos-count-leaves cmsis-freertos-message-queue-delete cmsis-freertos-thread-yield cmsis-freertos-kernel-state cmsis-freertos-kernel-lifecycle cmsis-freertos-mutex-delete cmsis-freertos-timer-running cmsis-freertos-sync-ops cmsis-freertos-sync-ops-candidate cmsis-freertos-timer-ops cmsis-freertos-timer-ops-candidate cmsis-freertos-event-flags cmsis-freertos-event-flags-candidate cmsis-freertos-timer-new cmsis-freertos-timer-new-candidate cmsis-freertos-memory-pool-new cmsis-freertos-memory-pool-new-candidate cmsis-freertos-semaphore-acquire cmsis-freertos-memory-pool-ops cmsis-freertos-message-queue-put cmsis-freertos-message-queue-get cmsis-freertos-delay cmsis-freertos-thread-set-priority cmsis-freertos-thread-terminate cmsis-freertos-thread-flags cmsis-freertos-thread-new cmsis-freertos-thread-yield-candidate cmsis-freertos-kernel-state-candidate cmsis-freertos-mutex-delete-candidate cmsis-freertos-timer-running-candidate lz4-snapshot freetype-snapshot flashdb-snapshot cmbacktrace-snapshot nanopb-snapshot cordio-aggregate-closure apollo-origin-accounting lvgl-display-port-closure third-party-dependency-closure lvgl-snapshot nemagfx-ambiq-provenance ambiq-gpu-patch-accessors-candidate ring-buffer-snapshot tinyframe-snapshot tinyframe-adapter-candidate ui-quicklist-page-closure ui-widget-news-page-closure ui-stock-page-closure research-corpus verify test inspect clean toolchain cjson-snapshot
.PHONY: ble-transport-profiles-closure ble-peer-discovery-closure ble-central-closure ble-connect-params-closure ble-peripheral-closure transport-protocol-closure service-settings-closure tracepoint-settings-closure product-rtos-closure util-error-check-closure goodix-v170-source-overlap logger-settings-closure ambiqsuite-cordio-app-snapshot cordio-app-framework-lineage drv-gx8002b-closure drv-pdm-production-closure drv-pdm-closure drv-mx25u25643g-closure service-ancc-closure als-closure thread-ble-production-closure pt-protocol-closure service-db-api-closure ui-even-ai-closure service-time-closure thread-audio-closure compress-log-core-closure compress-log-port-closure file-runtime-closure service-algo-closure uart-sync-closure service-nvdb-closure production-mic-closure service-audio-manager-closure service-audio-closure service-kvdb-closure ux-battery-sync-closure cb-ring-battery-closure callback-facades-closure callback-manager-closure silent-mode-closure onboarding-data-manager-closure onboarding-controller-closure onboarding-main-page-closure onboarding-stock-page-closure onboarding-news-page-closure lvgl-font-manager-closure common-list-container-closure common-text-container-closure evenhub-ui-closure evenhub-data-parser-closure sync-framework-closure sync-interface-api-closure display-thread-closure displaydrv-manager-closure ui-msg-notif-list-closure dashboard-main-screen-closure dashboard-watchface-layout4-closure dashboard-ext-closure dashboard-data-process-closure navigation-data-handler-closure navigation-ui-closure menu-page-closure ui-health-page-closure teleprompt-ui-closure service-em9305-dfu-closure conversate-tag-data-closure liblc3-source-closure
.PHONY: ambiqsuite-amota-snapshot ble-ota-ring-profiles-closure ring-service-closure service-input-manager-closure ui-calendar-page-closure ota-transport-closure efs-transport-closure evenhub-loading-page-closure dashboard-watchface-layout1-closure teleprompt-fsm-closure health-data-manager-closure evenhub-main-closure translate-closure translate-ui-closure teleprompt-controller-closure conversate-comm-data-closure conversate-controller-closure conversate-ui-main-page-closure service-universal-setting-closure common-image-container-closure dashboard-watchface-layout2-closure dashboard-watchface-layout3-closure thread-ring-closure fw-event-loop-closure ring-connect-policy-closure system-close-closure

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

freertos-g2-tcb-patch: freertos-snapshot
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_g2_freertos_tcb_patch

ambiqsuite-snapshot:
	$(PYTHON) $(AMBIQSUITE_DIR)/verify_snapshot.py

ambiqsuite-ancc-snapshot:
	$(PYTHON) $(AMBIQSUITE_ANCC_DIR)/verify_snapshot.py

ambiqsuite-amota-snapshot:
	$(PYTHON) $(AMBIQSUITE_AMOTA_DIR)/verify_snapshot.py

cmsis-core-snapshot:
	$(PYTHON) $(CMSIS_CORE_DIR)/verify_snapshot.py

cmsis-freertos-snapshot:
	$(PYTHON) $(CMSIS_FREERTOS_DIR)/verify_snapshot.py

cmsis-freertos-linked-census: cmsis-freertos-snapshot
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_cmsis_freertos_linked_census

cmsis-freertos-core-leaves: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_core_leaves

cmsis-freertos-count-leaves: cmsis-freertos-core-leaves
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_count_leaves

cmsis-freertos-message-queue-delete: cmsis-freertos-count-leaves
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_message_queue_delete

cmsis-freertos-thread-yield: cmsis-freertos-message-queue-delete
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_thread_yield

cmsis-freertos-kernel-state: cmsis-freertos-message-queue-delete
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_kernel_get_state

cmsis-freertos-mutex-delete: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_mutex_delete

cmsis-freertos-timer-running: cmsis-freertos-message-queue-delete
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_timer_is_running

cmsis-freertos-sync-ops: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_sync_ops

cmsis-freertos-sync-ops-candidate: cmsis-freertos-sync-ops

cmsis-freertos-timer-ops: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_timer_ops

cmsis-freertos-timer-ops-candidate: cmsis-freertos-timer-ops

cmsis-freertos-event-flags: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_event_flags

cmsis-freertos-event-flags-candidate: cmsis-freertos-event-flags

cmsis-freertos-timer-new: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_timer_new

cmsis-freertos-timer-new-candidate: cmsis-freertos-timer-new

cmsis-freertos-memory-pool-new: cmsis-freertos-linked-census
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_memory_pool_new

cmsis-freertos-memory-pool-new-candidate: cmsis-freertos-memory-pool-new

freertos-queue-receive-from-isr: freertos-snapshot
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_freertos_queue_receive_from_isr

cmsis-freertos-semaphore-acquire: cmsis-freertos-linked-census freertos-queue-receive-from-isr
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_semaphore_acquire

cmsis-freertos-memory-pool-ops: cmsis-freertos-memory-pool-new cmsis-freertos-semaphore-acquire
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_memory_pool_ops

freertos-queue-send-from-isr: freertos-snapshot
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_freertos_queue_send_from_isr

cmsis-freertos-message-queue-put: cmsis-freertos-linked-census freertos-queue-send-from-isr
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_message_queue_put

freertos-queue-receive: freertos-queue-receive-from-isr
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_freertos_queue_receive

cmsis-freertos-message-queue-get: cmsis-freertos-linked-census freertos-queue-receive
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_message_queue_get

cmsis-freertos-delay: cmsis-freertos-linked-census freertos-queue-receive
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_delay

cmsis-freertos-thread-set-priority: cmsis-freertos-delay
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_thread_set_priority

cmsis-freertos-thread-terminate: cmsis-freertos-thread-set-priority
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_thread_terminate

cmsis-freertos-thread-flags: cmsis-freertos-thread-terminate
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_thread_flags

cmsis-freertos-thread-new: cmsis-freertos-thread-flags
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_thread_new

cmsis-freertos-kernel-lifecycle: cmsis-freertos-thread-new cmsis-freertos-kernel-state
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_cmsis_kernel_lifecycle

cmsis-freertos-thread-yield-candidate: cmsis-freertos-thread-yield
cmsis-freertos-kernel-state-candidate: cmsis-freertos-kernel-state
cmsis-freertos-mutex-delete-candidate: cmsis-freertos-mutex-delete
cmsis-freertos-timer-running-candidate: cmsis-freertos-timer-running

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
	$(PYTHON) third_party/packetcraft-gatt-profile/verify_snapshot.py

ambiqsuite-cordio-app-snapshot:
	$(PYTHON) $(AMBIQSUITE_CORDIO_APP_DIR)/verify_snapshot.py

cordio-app-framework-lineage: ambiqsuite-cordio-app-snapshot
	$(PYTHON) tools/analyze_g2_cordio_app_framework.py \
		--ghidra-corpus "$${OPENCFW_APOLLO_GHIDRA_CORPUS:-/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth}"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_ambiqsuite_cordio_app_framework_snapshot \
		tests.test_analyze_g2_cordio_app_framework

cordio-aggregate-closure: cordio-app-framework-lineage
	$(PYTHON) tools/analyze_g2_cordio_closure.py \
		--ghidra-corpus "$${OPENCFW_APOLLO_GHIDRA_CORPUS:-/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth}"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_cordio_closure

lvgl-display-port-closure: core-component
	$(PYTHON) tools/analyze_g2_lvgl_display_port_closure.py \
		--component-report "components/apollo_main/core_overlay/build/build-report.json" \
		--ghidra-corpus "$${OPENCFW_APOLLO_GHIDRA_CORPUS:-/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth}"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_lvgl_display_port_closure

freertos-plus-cli-snapshot:
	$(PYTHON) $(FREERTOS_PLUS_CLI_DIR)/verify_snapshot.py

lvgl-snapshot:
	$(PYTHON) $(LVGL_DIR)/verify_snapshot.py

nemagfx-ambiq-provenance:
	$(PYTHON) tools/analyze_g2_nemagfx_ambiq_provenance.py

ambiq-gpu-patch-accessors-candidate: nemagfx-ambiq-provenance
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_ambiq_gpu_patch_accessors_candidate \
		tests.test_runtime_ambiq_gpu_patch_dashline_candidate \
		tests.test_runtime_ambiq_gpu_patch_get_glyph_candidate \
		tests.test_runtime_ambiq_gpu_patch_gradient_candidate \
		tests.test_runtime_ambiq_gpu_patch_shadow_blur_candidate \
		tests.test_runtime_ambiq_gpu_patch_small_raster_candidate \
		tests.test_runtime_ambiq_gpu_patch_shadow_blur_vg_candidate \
		tests.test_runtime_ambiq_gpu_patch_bitmap_glyph_candidate

ambiq-nema-hal-candidate:
	$(PYTHON) tools/analyze_g2_nema_hal.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_runtime_ambiq_nema_hal_candidate

ring-buffer-snapshot:
	$(PYTHON) $(RING_BUFFER_DIR)/verify_snapshot.py

tinyframe-snapshot:
	$(PYTHON) $(TINYFRAME_DIR)/verify_snapshot.py

cjson-snapshot:
	$(PYTHON) $(CJSON_DIR)/verify_snapshot.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_cjson_snapshot

tinyframe-adapter-candidate: tinyframe-snapshot
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_tinyframe_send_version \
		tests.test_tinyframe_snapshot \
		tests.test_tinyframe_g2_adapter_candidate \
		tests.test_tinyframe_g2_production_ports_candidate \
		tests.test_tinyframe_g2_atomic_boundary_candidate

vendor-snapshots: tlsf-snapshot easylogger-snapshot littlefs-snapshot freertos-snapshot ambiqsuite-snapshot ambiqsuite-ancc-snapshot ambiqsuite-amota-snapshot ambiqsuite-cordio-app-snapshot cmsis-core-snapshot cmsis-freertos-snapshot lz4-snapshot freetype-snapshot flashdb-snapshot cmbacktrace-snapshot nanopb-snapshot cordio-snapshot freertos-plus-cli-snapshot lvgl-snapshot ring-buffer-snapshot tinyframe-snapshot cjson-snapshot

upstream-audits:
	$(PYTHON) tools/analyze_g2_littlefs_ports.py
	$(PYTHON) tools/analyze_g2_littlefs_mspi_transport.py
	$(PYTHON) tools/analyze_g2_mspi_interrupt_clear.py
	$(PYTHON) tools/analyze_g2_freertos_port.py
	$(PYTHON) tools/analyze_g2_freertos_tcb_patch.py
	$(PYTHON) tools/analyze_g2_freertos_assert_port_seam.py
	$(PYTHON) tools/analyze_g2_freertos_ntz_context_handlers.py
	$(PYTHON) tools/analyze_g2_cmsis_freertos_linked_census.py
	$(PYTHON) tools/analyze_g2_nema_hal.py
	$(PYTHON) tools/analyze_g2_flashdb.py
	$(PYTHON) tools/analyze_g2_cmbacktrace_version.py
	$(PYTHON) tools/analyze_g2_nanopb_point_release.py
	$(PYTHON) tools/analyze_g2_nanopb_skip_field.py
	$(PYTHON) tools/analyze_g2_nanopb_raw_substream.py
	$(PYTHON) tools/analyze_g2_nanopb_bool_cluster.py
	$(PYTHON) tools/analyze_g2_nanopb_dec_varint.py
	$(PYTHON) tools/analyze_g2_nanopb_dec_bytes.py
	$(PYTHON) tools/analyze_g2_nanopb_dec_string.py
	$(PYTHON) tools/analyze_g2_nanopb_dec_submessage.py
	$(PYTHON) tools/analyze_g2_nanopb_decode_inner.py
	$(PYTHON) tools/analyze_g2_nanopb_decode_tag.py
	$(PYTHON) tools/analyze_g2_nanopb_field_default.py
	$(PYTHON) tools/analyze_g2_nanopb_iterator_cluster.py
	$(PYTHON) tools/analyze_g2_nanopb_message_defaults.py
	$(PYTHON) tools/analyze_g2_nanopb_field_decoder_cluster.py
	$(PYTHON) tools/analyze_g2_cordio_version.py
	$(PYTHON) tools/analyze_g2_freertos_plus_cli.py
	$(PYTHON) tools/analyze_g2_lvgl_version.py
	$(PYTHON) tools/analyze_g2_nemagfx_ambiq_provenance.py
	$(PYTHON) tools/analyze_g2_tinyframe_send_version.py
	$(PYTHON) tools/analyze_g2_ring_buffer.py

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

apollo-origin-accounting: source
	$(PYTHON) tools/analyze_g2_apollo_origin_accounting.py \
		--flash-plan "$(SOURCE_BUILD_DIR)/flash-plan.json" \
		--component-report "components/apollo_main/core_overlay/build/build-report.json" \
		--ghidra-corpus "$${OPENCFW_APOLLO_GHIDRA_CORPUS:-/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth}"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_apollo_origin_accounting

third-party-dependency-closure: source
	$(PYTHON) tools/analyze_g2_third_party_dependency_closure.py \
		--flash-plan "$(SOURCE_BUILD_DIR)/flash-plan.json" \
		--component-report "components/apollo_main/core_overlay/build/build-report.json" \
		--ghidra-corpus "$${OPENCFW_APOLLO_GHIDRA_CORPUS:-/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth}"
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_third_party_dependency_closure

pdt-distortion-test-closure:
	$(PYTHON) tools/analyze_g2_pdt_distortion_test.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_pdt_distortion_test \
		tests.test_analyze_g2_first_party_frontier

pdt-gray-screen-closure:
	$(PYTHON) tools/analyze_g2_pdt_gray_screen.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_pdt_gray_screen \
		tests.test_analyze_g2_first_party_frontier

production-test-screen-closure:
	$(PYTHON) tools/analyze_g2_production_test_screen.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_production_test_screen \
		tests.test_analyze_g2_first_party_frontier

cordio-gatt-profile-closure:
	$(PYTHON) third_party/packetcraft-gatt-profile/verify_snapshot.py
	$(PYTHON) tools/analyze_g2_cordio_gatt_profile.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_cordio_profile_gatt_snapshot \
		tests.test_analyze_g2_cordio_gatt_profile \
		tests.test_analyze_g2_first_party_frontier

ambiqsuite-ancc-profile-closure: ambiqsuite-ancc-snapshot
	$(PYTHON) tools/analyze_g2_ambiqsuite_ancc_profile.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_ambiqsuite_ancc_profile_snapshot \
		tests.test_analyze_g2_ambiqsuite_ancc_profile \
		tests.test_analyze_g2_first_party_frontier

ble-transport-profiles-closure:
	$(PYTHON) tools/analyze_g2_ble_transport_profiles.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ble_transport_profiles \
		tests.test_analyze_g2_first_party_frontier

ble-peer-discovery-closure:
	$(PYTHON) tools/analyze_g2_app_ble_peer_manager.py
	$(PYTHON) tools/analyze_g2_app_ble_discovery.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_app_ble_peer_manager \
		tests.test_analyze_g2_app_ble_discovery \
		tests.test_analyze_g2_first_party_frontier

ble-central-closure:
	$(PYTHON) tools/analyze_g2_app_ble_central.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_app_ble_central \
		tests.test_analyze_g2_first_party_frontier

ble-connect-params-closure:
	$(PYTHON) tools/analyze_g2_app_connect_params.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_app_connect_params \
		tests.test_analyze_g2_first_party_frontier

ble-peripheral-closure:
	$(PYTHON) tools/analyze_g2_app_ble_peripheral.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_app_ble_peripheral \
		tests.test_analyze_g2_first_party_frontier

transport-protocol-closure:
	$(PYTHON) tools/analyze_g2_transport_protocol.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_transport_protocol \
		tests.test_analyze_g2_first_party_frontier

service-settings-closure:
	$(PYTHON) tools/analyze_g2_service_settings.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_settings \
		tests.test_analyze_g2_first_party_frontier

tracepoint-settings-closure:
	$(PYTHON) tools/analyze_g2_tracepoint_setting.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_tracepoint_setting \
		tests.test_analyze_g2_first_party_frontier

product-rtos-closure:
	$(PYTHON) tools/analyze_g2_product_rtos.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_product_rtos \
		tests.test_analyze_g2_first_party_frontier

util-error-check-closure:
	$(PYTHON) tools/analyze_g2_util_error_check.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_util_error_check \
		tests.test_analyze_g2_first_party_frontier

goodix-v170-source-overlap:
	$(PYTHON) tools/analyze_g2_goodix_v170_source_overlap.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_goodix_v170_source_overlap

logger-settings-closure:
	$(PYTHON) tools/analyze_g2_logger_setting.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_logger_setting \
		tests.test_analyze_g2_first_party_frontier

ux-system-closure:
	$(PYTHON) tools/analyze_g2_ux_system.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ux_system \
		tests.test_analyze_g2_first_party_frontier

health-closure:
	$(PYTHON) tools/analyze_g2_health.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_health \
		tests.test_analyze_g2_first_party_frontier

quicklist-closure:
	$(PYTHON) tools/analyze_g2_quicklist.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_quicklist \
		tests.test_analyze_g2_first_party_frontier

dashboard-watchface-manager-closure:
	$(PYTHON) tools/analyze_g2_dashboard_watchface_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_watchface_manager \
		tests.test_analyze_g2_first_party_frontier

text-stream-service-closure:
	$(PYTHON) tools/analyze_g2_text_stream_service.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_text_stream_service \
		tests.test_analyze_g2_first_party_frontier

terminal-core-closure:
	$(PYTHON) tools/analyze_g2_terminal_core.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_terminal_core \
		tests.test_analyze_g2_first_party_frontier

drv-rtc-closure:
	$(PYTHON) tools/analyze_g2_drv_rtc.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_drv_rtc \
		tests.test_analyze_g2_first_party_frontier

teleprompt-file-list-closure:
	$(PYTHON) tools/analyze_g2_teleprompt_file_list.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_teleprompt_file_list \
		tests.test_analyze_g2_first_party_frontier

even-ai-timer-closure:
	$(PYTHON) tools/analyze_g2_even_ai_timer.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_even_ai_timer \
		tests.test_analyze_g2_first_party_frontier

cb-ble-status-closure:
	$(PYTHON) tools/analyze_g2_cb_ble_status.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_cb_ble_status \
		tests.test_analyze_g2_first_party_frontier

conversate-ui-menu-page-closure:
	$(PYTHON) tools/analyze_g2_conversate_ui_menu_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_ui_menu_page \
		tests.test_analyze_g2_first_party_frontier

conversate-ui-tag-page-closure:
	$(PYTHON) tools/analyze_g2_conversate_ui_tag_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_ui_tag_page \
		tests.test_analyze_g2_first_party_frontier

exit-prompt-closure:
	$(PYTHON) tools/analyze_g2_exit_prompt.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_exit_prompt \
		tests.test_analyze_g2_first_party_frontier

at-core-closure:
	$(PYTHON) tools/analyze_g2_at_core.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_at_core \
		tests.test_analyze_g2_first_party_frontier

hal-i2c-closure:
	$(PYTHON) tools/analyze_g2_hal_i2c.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_hal_i2c \
		tests.test_analyze_g2_first_party_frontier

service-ring-battery-closure:
	$(PYTHON) tools/analyze_g2_service_ring_battery.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_ring_battery \
		tests.test_analyze_g2_first_party_frontier

opt3007-registers-closure:
	$(PYTHON) tools/analyze_g2_opt3007_registers.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_opt3007_registers \
		tests.test_analyze_g2_first_party_frontier

service-codec-porting-closure:
	$(PYTHON) tools/analyze_g2_service_codec_porting.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_codec_porting \
		tests.test_analyze_g2_first_party_frontier

thread-notification-closure:
	$(PYTHON) tools/analyze_g2_thread_notification.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_thread_notification \
		tests.test_analyze_g2_first_party_frontier

drv-gx8002b-closure:
	$(PYTHON) tools/analyze_g2_drv_gx8002b.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_drv_gx8002b \
		tests.test_analyze_g2_first_party_frontier

service-db-api-closure:
	$(PYTHON) tools/analyze_g2_service_db_api.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_db_api \
		tests.test_analyze_g2_first_party_frontier

ui-even-ai-closure:
	$(PYTHON) tools/analyze_g2_ui_even_ai.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_even_ai \
		tests.test_analyze_g2_first_party_frontier

service-time-closure:
	$(PYTHON) tools/analyze_g2_service_time.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_time \
		tests.test_analyze_g2_first_party_frontier

thread-audio-closure:
	$(PYTHON) tools/analyze_g2_thread_audio.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_thread_audio \
		tests.test_analyze_g2_first_party_frontier

compress-log-core-closure:
	$(PYTHON) tools/analyze_g2_compress_log_core.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_compress_log_core \
		tests.test_analyze_g2_first_party_frontier

compress-log-port-closure:
	$(PYTHON) tools/analyze_g2_compress_log_port.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_compress_log_port \
		tests.test_analyze_g2_first_party_frontier

file-runtime-closure:
	$(PYTHON) tools/analyze_g2_file_runtime.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_file_runtime \
		tests.test_analyze_g2_first_party_frontier

service-algo-closure:
	$(PYTHON) tools/analyze_g2_service_algo.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_algo \
		tests.test_analyze_g2_first_party_frontier

uart-sync-closure:
	$(PYTHON) tools/analyze_g2_uart_sync.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_uart_sync \
		tests.test_analyze_g2_first_party_frontier

service-nvdb-closure:
	$(PYTHON) tools/analyze_g2_service_nvdb.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_nvdb \
		tests.test_analyze_g2_first_party_frontier

production-mic-closure:
	$(PYTHON) tools/analyze_g2_production_mic.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_production_mic \
		tests.test_analyze_g2_first_party_frontier

service-audio-manager-closure:
	$(PYTHON) tools/analyze_g2_service_audio_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_audio_manager \
		tests.test_analyze_g2_first_party_frontier

service-kvdb-closure:
	$(PYTHON) tools/analyze_g2_service_kvdb.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_kvdb \
		tests.test_analyze_g2_flashdb \
		tests.test_analyze_g2_first_party_frontier

ux-battery-sync-closure:
	$(PYTHON) tools/analyze_g2_ux_battery_sync.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ux_battery_sync \
		tests.test_analyze_g2_first_party_frontier

cb-ring-battery-closure:
	$(PYTHON) tools/analyze_g2_cb_ring_battery.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_cb_ring_battery \
		tests.test_analyze_g2_ux_battery_sync \
		tests.test_analyze_g2_first_party_frontier

callback-facades-closure:
	$(PYTHON) tools/analyze_g2_callback_facades.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_callback_facades \
		tests.test_analyze_g2_first_party_frontier

callback-manager-closure:
	$(PYTHON) tools/analyze_g2_callback_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_callback_manager \
		tests.test_analyze_g2_callback_facades \
		tests.test_analyze_g2_cb_ring_battery \
		tests.test_analyze_g2_first_party_frontier

silent-mode-closure:
	$(PYTHON) tools/analyze_g2_silent_mode.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_silent_mode \
		tests.test_analyze_g2_first_party_frontier

onboarding-data-manager-closure:
	$(PYTHON) tools/analyze_g2_onboarding_data_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_onboarding_data_manager \
		tests.test_analyze_g2_first_party_frontier

onboarding-controller-closure:
	$(PYTHON) tools/analyze_g2_onboarding_controller.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_onboarding_controller \
		tests.test_analyze_g2_onboarding_data_manager \
		tests.test_analyze_g2_first_party_frontier

onboarding-main-page-closure:
	$(PYTHON) tools/analyze_g2_onboarding_main_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_onboarding_main_page \
		tests.test_analyze_g2_onboarding_controller \
		tests.test_analyze_g2_first_party_frontier

onboarding-stock-page-closure:
	$(PYTHON) tools/analyze_g2_onboarding_stock_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_onboarding_stock_page \
		tests.test_analyze_g2_onboarding_main_page \
		tests.test_analyze_g2_first_party_frontier

onboarding-news-page-closure:
	$(PYTHON) tools/analyze_g2_onboarding_news_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_onboarding_news_page \
		tests.test_analyze_g2_onboarding_stock_page \
		tests.test_analyze_g2_first_party_frontier

lvgl-font-manager-closure:
	$(PYTHON) tools/analyze_g2_lvgl_font_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_lvgl_font_manager \
		tests.test_freetype_g2_config_audit \
		tests.test_analyze_g2_first_party_frontier

common-list-container-closure:
	$(PYTHON) tools/analyze_g2_common_list_container.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_common_list_container \
		tests.test_analyze_g2_first_party_frontier

common-text-container-closure:
	$(PYTHON) tools/analyze_g2_common_text_container.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_common_text_container \
		tests.test_analyze_g2_first_party_frontier

evenhub-ui-closure:
	$(PYTHON) tools/analyze_g2_evenhub_ui.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_evenhub_ui \
		tests.test_analyze_g2_first_party_frontier

evenhub-data-parser-closure:
	$(PYTHON) tools/analyze_g2_evenhub_data_parser.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_evenhub_data_parser \
		tests.test_analyze_g2_first_party_frontier

sync-framework-closure:
	$(PYTHON) tools/analyze_g2_sync_framework.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_sync_framework \
		tests.test_analyze_g2_first_party_frontier

sync-interface-api-closure:
	$(PYTHON) tools/analyze_g2_sync_interface_api.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_sync_interface_api \
		tests.test_analyze_g2_first_party_frontier

display-thread-closure:
	$(PYTHON) tools/analyze_g2_display_thread.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_display_thread \
		tests.test_analyze_g2_first_party_frontier

drv-mx25u25643g-closure:
	$(PYTHON) tools/analyze_g2_drv_mx25u25643g.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_drv_mx25u25643g \
		tests.test_analyze_g2_first_party_frontier

ui-msg-notif-list-closure:
	$(PYTHON) tools/analyze_g2_ui_msg_notif_list.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_msg_notif_list \
		tests.test_analyze_g2_first_party_frontier

dashboard-main-screen-closure:
	$(PYTHON) tools/analyze_g2_dashboard_main_screen.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_main_screen \
		tests.test_analyze_g2_first_party_frontier

dashboard-watchface-layout4-closure:
	$(PYTHON) tools/analyze_g2_dashboard_watchface_layout4.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_watchface_layout4 \
		tests.test_analyze_g2_first_party_frontier

dashboard-ext-closure:
	$(PYTHON) tools/analyze_g2_dashboard_ext.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_ext \
		tests.test_analyze_g2_first_party_frontier

dashboard-data-process-closure:
	$(PYTHON) tools/analyze_g2_dashboard_data_process.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_data_process \
		tests.test_analyze_g2_first_party_frontier

displaydrv-manager-closure:
	$(PYTHON) tools/analyze_g2_displaydrv_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_displaydrv_manager \
		tests.test_analyze_g2_first_party_frontier

npmx-main-driver-closure:
	$(PYTHON) third_party/npmx/verify_snapshot.py
	$(PYTHON) tools/analyze_g2_npmx_main_driver.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_npmx_main_driver \
		tests.test_analyze_g2_first_party_frontier

liblc3-source-closure:
	$(PYTHON) third_party/liblc3/verify_snapshot.py
	$(PYTHON) tools/analyze_g2_liblc3.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_liblc3

service-audio-closure:
	$(PYTHON) tools/analyze_g2_service_audio.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_audio \
		tests.test_analyze_g2_first_party_frontier

drv-pdm-production-closure:
	$(PYTHON) tools/analyze_g2_drv_pdm_production.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_drv_pdm_production \
		tests.test_analyze_g2_first_party_frontier

drv-pdm-closure:
	$(PYTHON) tools/analyze_g2_drv_pdm.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_drv_pdm \
		tests.test_analyze_g2_first_party_frontier

service-ancc-closure:
	$(PYTHON) tools/analyze_g2_service_ancc.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_ancc \
		tests.test_analyze_g2_first_party_frontier

als-closure:
	$(PYTHON) tools/analyze_g2_als.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_als \
		tests.test_analyze_g2_first_party_frontier

thread-ble-production-closure:
	$(PYTHON) tools/analyze_g2_thread_ble_production.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_thread_ble_production \
		tests.test_analyze_g2_first_party_frontier

pt-protocol-closure:
	$(PYTHON) tools/analyze_g2_pt_protocol.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_pt_protocol \
		tests.test_analyze_g2_first_party_frontier

ui-quicklist-page-closure:
	$(PYTHON) tools/analyze_g2_ui_quicklist_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_quicklist_page \
		tests.test_analyze_g2_first_party_frontier

ui-widget-news-page-closure:
	$(PYTHON) tools/analyze_g2_ui_widget_news_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_widget_news_page \
		tests.test_analyze_g2_first_party_frontier

ui-stock-page-closure:
	$(PYTHON) tools/analyze_g2_ui_stock_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_stock_page \
		tests.test_analyze_g2_first_party_frontier

navigation-ui-closure:
	$(PYTHON) tools/analyze_g2_navigation_ui.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_navigation_ui \
		tests.test_analyze_g2_first_party_frontier

menu-page-closure:
	$(PYTHON) tools/analyze_g2_menu_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_menu_page \
		tests.test_analyze_g2_first_party_frontier

ui-health-page-closure:
	$(PYTHON) tools/analyze_g2_ui_health_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_health_page \
		tests.test_analyze_g2_first_party_frontier

ring-service-closure:
	$(PYTHON) tools/analyze_g2_ring_service.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ring_service \
		tests.test_analyze_g2_first_party_frontier

service-input-manager-closure:
	$(PYTHON) tools/analyze_g2_service_input_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_input_manager \
		tests.test_analyze_g2_first_party_frontier

ui-calendar-page-closure:
	$(PYTHON) tools/analyze_g2_ui_calendar_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ui_calendar_page \
		tests.test_analyze_g2_first_party_frontier

ota-transport-closure:
	$(PYTHON) tools/analyze_g2_ota_transport.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ota_transport \
		tests.test_analyze_g2_first_party_frontier

efs-transport-closure:
	$(PYTHON) tools/analyze_g2_efs_transport.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_efs_transport \
		tests.test_analyze_g2_first_party_frontier

evenhub-loading-page-closure:
	$(PYTHON) tools/analyze_g2_evenhub_loading_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_evenhub_loading_page \
		tests.test_analyze_g2_first_party_frontier

dashboard-watchface-layout1-closure:
	$(PYTHON) tools/analyze_g2_dashboard_watchface_layout1.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_watchface_layout1 \
		tests.test_analyze_g2_first_party_frontier

teleprompt-fsm-closure:
	$(PYTHON) tools/analyze_g2_teleprompt_fsm.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_teleprompt_fsm \
		tests.test_analyze_g2_first_party_frontier

health-data-manager-closure:
	$(PYTHON) tools/analyze_g2_health_data_manager.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_health_data_manager \
		tests.test_analyze_g2_first_party_frontier

evenhub-main-closure:
	$(PYTHON) tools/analyze_g2_evenhub_main.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_evenhub_main \
		tests.test_analyze_g2_first_party_frontier

translate-closure:
	$(PYTHON) tools/analyze_g2_translate.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_translate \
		tests.test_analyze_g2_first_party_frontier

translate-ui-closure:
	$(PYTHON) tools/analyze_g2_translate_ui.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_translate_ui \
		tests.test_analyze_g2_first_party_frontier

teleprompt-controller-closure:
	$(PYTHON) tools/analyze_g2_teleprompt_controller.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_teleprompt_controller \
		tests.test_analyze_g2_first_party_frontier

conversate-comm-data-closure:
	$(PYTHON) tools/analyze_g2_conversate_comm_data.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_comm_data \
		tests.test_analyze_g2_first_party_frontier

conversate-controller-closure:
	$(PYTHON) tools/analyze_g2_conversate_controller.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_controller \
		tests.test_analyze_g2_first_party_frontier

conversate-ui-main-page-closure:
	$(PYTHON) tools/analyze_g2_conversate_ui_main_page.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_ui_main_page \
		tests.test_analyze_g2_first_party_frontier

service-universal-setting-closure:
	$(PYTHON) tools/analyze_g2_service_universal_setting.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_universal_setting \
		tests.test_analyze_g2_first_party_frontier

common-image-container-closure:
	$(PYTHON) tools/analyze_g2_common_image_container.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_common_image_container \
		tests.test_analyze_g2_first_party_frontier

dashboard-watchface-layout2-closure:
	$(PYTHON) tools/analyze_g2_dashboard_watchface_layout2.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_watchface_layout2 \
		tests.test_analyze_g2_first_party_frontier

dashboard-watchface-layout3-closure:
	$(PYTHON) tools/analyze_g2_dashboard_watchface_layout3.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_dashboard_watchface_layout3 \
		tests.test_analyze_g2_first_party_frontier

thread-ring-closure:
	$(PYTHON) tools/analyze_g2_thread_ring.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_thread_ring \
		tests.test_analyze_g2_ble_ota_ring_profiles \
		tests.test_analyze_g2_first_party_frontier

fw-event-loop-closure:
	$(PYTHON) tools/analyze_g2_fw_event_loop.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_fw_event_loop \
		tests.test_analyze_g2_first_party_frontier

ring-connect-policy-closure:
	$(PYTHON) tools/analyze_g2_ring_connect_policy.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_ring_connect_policy \
		tests.test_analyze_g2_first_party_frontier

system-close-closure:
	$(PYTHON) tools/analyze_g2_system_close.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_system_close \
		tests.test_analyze_g2_service_settings \
		tests.test_analyze_g2_first_party_frontier

navigation-data-handler-closure:
	$(PYTHON) tools/analyze_g2_navigation_data_handler.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_navigation_data_handler \
		tests.test_analyze_g2_first_party_frontier

teleprompt-ui-closure:
	$(PYTHON) tools/analyze_g2_teleprompt_ui.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_teleprompt_ui \
		tests.test_analyze_g2_first_party_frontier

service-em9305-dfu-closure:
	$(PYTHON) tools/analyze_g2_service_em9305_dfu.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_service_em9305_dfu \
		tests.test_analyze_g2_first_party_frontier

conversate-tag-data-closure:
	$(PYTHON) tools/analyze_g2_conversate_tag_data.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_conversate_tag_data \
		tests.test_analyze_g2_first_party_frontier

legal-regulatory-closure:
	$(PYTHON) tools/analyze_g2_legal_regulatory.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_analyze_g2_legal_regulatory \
		tests.test_analyze_g2_first_party_frontier

ble-ota-ring-profiles-closure: ambiqsuite-amota-snapshot
	$(PYTHON) tools/analyze_g2_ble_ota_ring_profiles.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v \
		tests.test_ambiqsuite_amota_profile_snapshot \
		tests.test_analyze_g2_ble_ota_ring_profiles \
		tests.test_analyze_g2_first_party_frontier

research-corpus:
	$(PYTHON) tools/verify_research_corpus.py

verify: ring-component bootloader-component core-component upstream-audits research-corpus
	$(PYTHON) tools/open_cfw.py verify --manifest "$(REFERENCE_MANIFEST)"
	$(PYTHON) tools/open_cfw.py verify --manifest "$(RING_SOURCE_MANIFEST)"
	$(PYTHON) tools/open_cfw.py verify --manifest "$(SOURCE_MANIFEST)"

test: ring-component bootloader-component core-component
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v

inspect: source
	$(PYTHON) -m json.tool "$(SOURCE_BUILD_DIR)/flash-plan.json"

clean:
	$(PYTHON) -c 'from pathlib import Path; import shutil; root=Path.cwd().resolve(); targets=tuple((root/path).resolve() for path in ("build", "$(RING_COMPONENT_BUILD_DIR)", "$(CORE_COMPONENT_BUILD_DIR)", "$(BOOT_COMPONENT_BUILD_DIR)")); assert all(root in path.parents and path != root for path in targets); [shutil.rmtree(path, ignore_errors=True) for path in targets]'
