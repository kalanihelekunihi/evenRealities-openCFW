# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

list(APPEND BOARD_ROOT ${CMAKE_CURRENT_SOURCE_DIR})
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(openr1_zephyr)

if(SYSBUILD)
  zephyr_get(OPENR1_BMA456_ROOT SYSBUILD GLOBAL)
  zephyr_get(OPENR1_LIS2DW12_ROOT SYSBUILD GLOBAL)
  zephyr_get(OPENR1_ST25DVXXKC_ROOT SYSBUILD GLOBAL)
  zephyr_get(OPENR1_FLASHDB_ROOT SYSBUILD GLOBAL)
  zephyr_get(OPENR1_GOODIX_DEMOCODE_ROOT SYSBUILD GLOBAL)
endif()

get_filename_component(OPENR1_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../.." ABSOLUTE)

if(NOT DEFINED OPENR1_BMA456_ROOT OR
   NOT EXISTS "${OPENR1_BMA456_ROOT}/bma4.c" OR
   NOT EXISTS "${OPENR1_BMA456_ROOT}/bma456w.c")
  message(FATAL_ERROR "OPENR1_BMA456_ROOT must name the pinned Bosch BMA456 SensorAPI root")
endif()
if(NOT DEFINED OPENR1_LIS2DW12_ROOT OR
   NOT EXISTS "${OPENR1_LIS2DW12_ROOT}/lis2dw12_reg.c")
  message(FATAL_ERROR "OPENR1_LIS2DW12_ROOT must name the pinned ST LIS2DW12 provider root")
endif()
if(NOT DEFINED OPENR1_ST25DVXXKC_ROOT OR
   NOT EXISTS "${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc.c" OR
   NOT EXISTS "${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc_reg.c")
  message(FATAL_ERROR "OPENR1_ST25DVXXKC_ROOT must name the pinned ST25DVxxKC component root")
endif()
if(NOT DEFINED OPENR1_FLASHDB_ROOT OR
   NOT EXISTS "${OPENR1_FLASHDB_ROOT}/src/fdb.c" OR
   NOT EXISTS "${OPENR1_FLASHDB_ROOT}/src/fdb_tsdb.c" OR
   NOT EXISTS "${OPENR1_FLASHDB_ROOT}/port/fal/src/fal_partition.c")
  message(FATAL_ERROR "OPENR1_FLASHDB_ROOT must name pinned FlashDB 2.0.0 with bundled FAL 0.5.99")
endif()
if(NOT DEFINED OPENR1_GOODIX_DEMOCODE_ROOT OR
   NOT EXISTS "${OPENR1_GOODIX_DEMOCODE_ROOT}/LICENSE" OR
   NOT EXISTS "${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_kernel_code/kernel/gh_demo.c" OR
   NOT EXISTS "${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_kernel_code/driver/src/gh_drv_control.c")
  message(FATAL_ERROR "OPENR1_GOODIX_DEMOCODE_ROOT must name the pinned Goodix GH3X2X democode root")
endif()
get_filename_component(OPENR1_BMA456_ROOT "${OPENR1_BMA456_ROOT}" ABSOLUTE)
get_filename_component(OPENR1_LIS2DW12_ROOT "${OPENR1_LIS2DW12_ROOT}" ABSOLUTE)
get_filename_component(OPENR1_ST25DVXXKC_ROOT "${OPENR1_ST25DVXXKC_ROOT}" ABSOLUTE)
get_filename_component(OPENR1_FLASHDB_ROOT "${OPENR1_FLASHDB_ROOT}" ABSOLUTE)
get_filename_component(OPENR1_GOODIX_DEMOCODE_ROOT "${OPENR1_GOODIX_DEMOCODE_ROOT}" ABSOLUTE)

set(OPENR1_GOODIX_DRIVER_DIR
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_kernel_code/driver)
set(OPENR1_GOODIX_KERNEL_DIR
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_kernel_code/kernel)
set(OPENR1_GOODIX_MODULE_DIR
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_kernel_code/module)
set(OPENR1_GOODIX_ALGO_CALL_DIR
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_algo_code/goodix_algo_call/inc)
set(OPENR1_GOODIX_SOURCES
  ${OPENR1_GOODIX_DRIVER_DIR}/src/gh_drv_config.c
  ${OPENR1_GOODIX_DRIVER_DIR}/src/gh_drv_control.c
  ${OPENR1_GOODIX_DRIVER_DIR}/src/gh_drv_dump.c
  ${OPENR1_GOODIX_DRIVER_DIR}/src/gh_drv_interface.c
  ${OPENR1_GOODIX_KERNEL_DIR}/gh_demo.c
  ${OPENR1_GOODIX_KERNEL_DIR}/gh_demo_hook.c
  ${OPENR1_GOODIX_KERNEL_DIR}/gh_demo_reg_array.c
  ${OPENR1_GOODIX_KERNEL_DIR}/gh_demo_user.c
  ${OPENR1_GOODIX_MODULE_DIR}/gh_agc/gh_agc.c
  ${OPENR1_GOODIX_MODULE_DIR}/gh_other/gh_changeinttime.c
  ${OPENR1_GOODIX_MODULE_DIR}/gh_other/gh_movedetect.c
  ${OPENR1_GOODIX_MODULE_DIR}/gh_soft_adt/gh_multi_sen_pro.c
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/algo_lib/algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c
)

set(OPENR1_PORTABLE_SOURCES
  ${OPENR1_ROOT}/src/r1_crc.c
  ${OPENR1_ROOT}/src/r1_protocol.c
  ${OPENR1_ROOT}/src/r1_health.c
  ${OPENR1_ROOT}/src/r1_health_db.c
  ${OPENR1_ROOT}/src/r1_twi_sync.c
  ${OPENR1_ROOT}/src/r1_retained_log.c
  ${OPENR1_ROOT}/src/r1_reset_trace.c
  ${OPENR1_ROOT}/src/r1_reset_reason.c
  ${OPENR1_ROOT}/src/r1_state.c
  ${OPENR1_ROOT}/src/r1_storage.c
  ${OPENR1_ROOT}/src/r1_kv_store.c
  ${OPENR1_ROOT}/src/r1_nv_recovery.c
  ${OPENR1_ROOT}/src/r1_sleep_db.c
  ${OPENR1_ROOT}/src/r1_persistence.c
  ${OPENR1_ROOT}/src/r1_connection_params.c
  ${OPENR1_ROOT}/src/r1_peer_target.c
  ${OPENR1_ROOT}/src/r1_event.c
  ${OPENR1_ROOT}/src/r1_event_bus.c
  ${OPENR1_ROOT}/src/r1_dispatch.c
  ${OPENR1_ROOT}/src/r1_crypto.c
  ${OPENR1_ROOT}/src/r1_goodix.c
  ${OPENR1_ROOT}/src/r1_iqs7211e.c
  ${OPENR1_ROOT}/src/r1_st25dvxxkc.c
  ${OPENR1_ROOT}/src/r1_power_lease.c
  ${OPENR1_ROOT}/src/r1_battery.c
  ${OPENR1_ROOT}/src/r1_motion.c
  ${OPENR1_ROOT}/src/r1_wear.c
  ${OPENR1_ROOT}/src/r1_clock.c
  ${OPENR1_ROOT}/src/r1_runtime.c
  ${OPENR1_ROOT}/platform/nrf52840/r1_nrf52840.c
  ${OPENR1_ROOT}/port/r1_fal_port.c
  ${OPENR1_ROOT}/port/goodix_gh3x2x/r1_gh3x2x_port.c
)

set(OPENR1_RECONSTRUCTED_SOURCES
  ${OPENR1_ROOT}/reconstructed/rtc_device/rtc_device.c
  ${OPENR1_ROOT}/reconstructed/generic_device_registry/generic_device_registry.c
  ${OPENR1_ROOT}/reconstructed/software_twi/software_twi.c
  ${OPENR1_ROOT}/reconstructed/sensor_stream/sensor_stream.c
  ${OPENR1_ROOT}/reconstructed/time_calendar/time_calendar.c
  ${OPENR1_ROOT}/reconstructed/model_data/r1_model_data.c
  ${OPENR1_ROOT}/reconstructed/quantized_runtime/quantized_runtime.c
  ${OPENR1_ROOT}/reconstructed/gxt310/gxt310.c
  ${OPENR1_ROOT}/reconstructed/qma6100/qma6100.c
  ${OPENR1_ROOT}/reconstructed/yhm2710/yhm2710.c
  ${OPENR1_ROOT}/reconstructed/goodix_primitives/goodix_primitives.c
  ${OPENR1_ROOT}/reconstructed/goodix_heap/goodix_heap.c
  ${OPENR1_ROOT}/reconstructed/gomore_primitives/gomore_primitives.c
  ${OPENR1_ROOT}/reconstructed/gomore_tensor_runtime/gomore_tensor_runtime.c
)

target_sources(app PRIVATE
  src/main.c
  src/openr1_bae8_zephyr.c
  src/openr1_analog_zephyr.c
  src/openr1_clock_zephyr.c
  src/openr1_motion_zephyr.c
  src/openr1_nfc_zephyr.c
  src/openr1_nfc_resources_zephyr.c
  src/openr1_optical_zephyr.c
  src/openr1_power_zephyr.c
  src/openr1_reset_zephyr.c
  src/openr1_sensor_stream_zephyr.c
  src/openr1_storage_zephyr.c
  src/openr1_software_twi_zephyr.c
  src/openr1_temperature_zephyr.c
  src/openr1_touch_zephyr.c
  src/openr1_twim1_zephyr.c
  src/openr1_databases_zephyr.c
  src/openr1_watchdog_zephyr.c
  src/openr1_yhm2710_zephyr.c
  ${OPENR1_ROOT}/port/goodix_gh3x2x/r1_gh3x2x_bind.c
  ${OPENR1_ROOT}/port/goodix_gh3x2x/r1_gh3x2x_stubs.c
  ${OPENR1_PORTABLE_SOURCES}
  ${OPENR1_RECONSTRUCTED_SOURCES}
  ${OPENR1_BMA456_ROOT}/bma4.c
  ${OPENR1_BMA456_ROOT}/bma456w.c
  ${OPENR1_LIS2DW12_ROOT}/lis2dw12_reg.c
  ${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc.c
  ${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc_reg.c
  ${OPENR1_FLASHDB_ROOT}/src/fdb.c
  ${OPENR1_FLASHDB_ROOT}/src/fdb_tsdb.c
  ${OPENR1_FLASHDB_ROOT}/src/fdb_utils.c
  ${OPENR1_FLASHDB_ROOT}/port/fal/src/fal.c
  ${OPENR1_FLASHDB_ROOT}/port/fal/src/fal_flash.c
  ${OPENR1_FLASHDB_ROOT}/port/fal/src/fal_partition.c
  ${OPENR1_GOODIX_SOURCES}
)

target_include_directories(app PRIVATE
  ${OPENR1_ROOT}/include
  ${OPENR1_ROOT}/reconstructed
  ${OPENR1_ROOT}/port
  ${OPENR1_ROOT}/port/goodix_gh3x2x
  ${OPENR1_BMA456_ROOT}
  ${OPENR1_LIS2DW12_ROOT}
  ${OPENR1_ST25DVXXKC_ROOT}
  ${OPENR1_FLASHDB_ROOT}/inc
  ${OPENR1_FLASHDB_ROOT}/port/fal/inc
  ${OPENR1_ROOT}/port/goodix_gh3x2x/config
  ${OPENR1_GOODIX_DRIVER_DIR}/inc
  ${OPENR1_GOODIX_KERNEL_DIR}
  ${OPENR1_GOODIX_MODULE_DIR}/gh_agc
  ${OPENR1_GOODIX_MODULE_DIR}/gh_ecg
  ${OPENR1_GOODIX_MODULE_DIR}/gh_other
  ${OPENR1_GOODIX_MODULE_DIR}/gh_protocol
  ${OPENR1_GOODIX_MODULE_DIR}/gh_soft_adt
  ${OPENR1_GOODIX_DEMOCODE_ROOT}/demo_code/demo_algo_code/goodix_algo_application/inc
  ${OPENR1_GOODIX_ALGO_CALL_DIR}
  ${OPENR1_GOODIX_ALGO_CALL_DIR}/hr_exc
  ${OPENR1_GOODIX_ALGO_CALL_DIR}/spo2_pre_exc
)

# The stock-compatible dual AES adapter remains shared with the nRF5 target;
# this backend selects Zephyr's source-built TinyCrypt AES primitive.
target_compile_definitions(app PRIVATE
  R1_USE_TINYCRYPT=1
  __DATE__="Aug 14 2026"
  __TIME__="00:00:00"
)
target_compile_options(app PRIVATE -Wno-builtin-macro-redefined)

# Zephyr normally garbage-collects uncalled translation-unit sections. The
# reconstructed corpus is itself an auditable firmware deliverable, so retain
# every code and constant section from every reconstructed object.
zephyr_linker_sources(SECTIONS openr1_reconstructed.ld)
zephyr_linker_sources(SECTIONS openr1_goodix.ld)
zephyr_linker_sources(SECTIONS openr1_platform.ld)
