PROJECT_NAME := openr1_sdk
TARGETS := openr1_nrf52840_s140
OUTPUT_DIRECTORY ?= _build

ifndef SDK_ROOT
$(error SDK_ROOT must name the pinned nRF5_SDK_17.1.0_ddde560 directory)
endif
ifndef BMA456_ROOT
$(error BMA456_ROOT must name the pinned Bosch BMA456_SensorAPI v2.29.0 directory)
endif
ifndef LIS2DW12_ROOT
$(error LIS2DW12_ROOT must name the pinned ST lis2dw12-pid v2.1.0 directory)
endif
ifndef ST25DVXXKC_ROOT
$(error ST25DVXXKC_ROOT must name the pinned ST ST25DVxxKC component directory)
endif
ifndef TINY_AES_ROOT
$(error TINY_AES_ROOT must name the pinned tiny-AES-c v1.0.0-compatible directory)
endif
ifndef FLASHDB_ROOT
$(error FLASHDB_ROOT must name the pinned FlashDB 2.0.0 directory with bundled FAL 0.5.99)
endif

PROJ_DIR := $(abspath ../../..)
LINKER_SCRIPT := openr1_sdk.ld
CMSIS_FREERTOS_ROOT := $(abspath $(PROJ_DIR)/../g2/third_party/cmsis-freertos)
FREERTOS_KERNEL_ROOT := $(abspath $(PROJ_DIR)/../g2/third_party/freertos-kernel)
CMBACKTRACE_ROOT := $(abspath $(PROJ_DIR)/../g2/third_party/cmbacktrace)

OPENR1_SOURCES := \
  $(PROJ_DIR)/src/r1_crc.c \
  $(PROJ_DIR)/src/r1_protocol.c \
  $(PROJ_DIR)/src/r1_health.c \
  $(PROJ_DIR)/src/r1_health_db.c \
  $(PROJ_DIR)/src/r1_twi_sync.c \
  $(PROJ_DIR)/src/r1_retained_log.c \
  $(PROJ_DIR)/src/r1_reset_trace.c \
  $(PROJ_DIR)/src/r1_reset_reason.c \
  $(PROJ_DIR)/src/r1_state.c \
  $(PROJ_DIR)/src/r1_storage.c \
  $(PROJ_DIR)/src/r1_kv_store.c \
  $(PROJ_DIR)/src/r1_nv_recovery.c \
  $(PROJ_DIR)/src/r1_sleep_db.c \
  $(PROJ_DIR)/src/r1_persistence.c \
  $(PROJ_DIR)/src/r1_connection_params.c \
  $(PROJ_DIR)/src/r1_peer_target.c \
  $(PROJ_DIR)/src/r1_event.c \
  $(PROJ_DIR)/src/r1_dispatch.c \
  $(PROJ_DIR)/src/r1_crypto.c \
  $(PROJ_DIR)/src/r1_goodix.c \
  $(PROJ_DIR)/src/r1_iqs7211e.c \
  $(PROJ_DIR)/src/r1_st25dvxxkc.c \
  $(PROJ_DIR)/src/r1_power_lease.c \
  $(PROJ_DIR)/src/r1_battery.c \
  $(PROJ_DIR)/src/r1_motion.c \
  $(PROJ_DIR)/src/r1_wear.c \
  $(PROJ_DIR)/src/r1_runtime.c \
  $(PROJ_DIR)/platform/nrf52840/r1_nrf52840.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_advertising.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_analog.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_app_timer_compat.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_bae8.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_cmbacktrace_port.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_gatt.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_health.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_health_db.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_twi_sync.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_retained_log.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_reset_trace_port.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_reset_reason.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_i2c5_resources.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_motion.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_nfc.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_peer.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_scheduler.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_storage.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_touch.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_watchdog.c \
  $(PROJ_DIR)/port/r1_fal_port.c \
  $(PROJ_DIR)/platform/nrf52840/sdk/main.c

SRC_FILES += \
  $(SDK_ROOT)/modules/nrfx/mdk/gcc_startup_nrf52840.S \
  $(PROJ_DIR)/platform/nrf52840/sdk/openr1_cmbacktrace_fault.S \
  $(SDK_ROOT)/modules/nrfx/mdk/system_nrf52840.c \
  $(SDK_ROOT)/external/segger_rtt/SEGGER_RTT.c \
  $(SDK_ROOT)/components/libraries/util/app_error.c \
  $(SDK_ROOT)/components/libraries/util/app_error_handler_gcc.c \
  $(SDK_ROOT)/components/libraries/util/app_error_weak.c \
  $(SDK_ROOT)/components/libraries/util/app_util_platform.c \
  $(SDK_ROOT)/components/libraries/experimental_section_vars/nrf_section_iter.c \
  $(SDK_ROOT)/components/libraries/atomic/nrf_atomic.c \
  $(SDK_ROOT)/components/libraries/atomic_flags/nrf_atflags.c \
  $(SDK_ROOT)/components/libraries/atomic_fifo/nrf_atfifo.c \
  $(SDK_ROOT)/components/libraries/fds/fds.c \
  $(SDK_ROOT)/components/libraries/fstorage/nrf_fstorage.c \
  $(SDK_ROOT)/components/libraries/fstorage/nrf_fstorage_sd.c \
  $(SDK_ROOT)/components/libraries/sortlist/nrf_sortlist.c \
  $(SDK_ROOT)/components/libraries/strerror/nrf_strerror.c \
  $(SDK_ROOT)/components/libraries/timer/app_timer_freertos.c \
  $(SDK_ROOT)/components/ble/ble_advertising/ble_advertising.c \
  $(SDK_ROOT)/components/ble/common/ble_advdata.c \
  $(SDK_ROOT)/components/ble/common/ble_conn_state.c \
  $(SDK_ROOT)/components/ble/common/ble_srv_common.c \
  $(SDK_ROOT)/components/ble/nrf_ble_gatt/nrf_ble_gatt.c \
  $(SDK_ROOT)/components/ble/peer_manager/auth_status_tracker.c \
  $(SDK_ROOT)/components/ble/peer_manager/gatt_cache_manager.c \
  $(SDK_ROOT)/components/ble/peer_manager/gatts_cache_manager.c \
  $(SDK_ROOT)/components/ble/peer_manager/id_manager.c \
  $(SDK_ROOT)/components/ble/peer_manager/peer_data_storage.c \
  $(SDK_ROOT)/components/ble/peer_manager/peer_database.c \
  $(SDK_ROOT)/components/ble/peer_manager/peer_id.c \
  $(SDK_ROOT)/components/ble/peer_manager/peer_manager.c \
  $(SDK_ROOT)/components/ble/peer_manager/peer_manager_handler.c \
  $(SDK_ROOT)/components/ble/peer_manager/pm_buffer.c \
  $(SDK_ROOT)/components/ble/peer_manager/security_dispatcher.c \
  $(SDK_ROOT)/components/ble/peer_manager/security_manager.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh_ble.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh_soc.c \
  $(FREERTOS_KERNEL_ROOT)/event_groups.c \
  $(FREERTOS_KERNEL_ROOT)/list.c \
  $(FREERTOS_KERNEL_ROOT)/queue.c \
  $(FREERTOS_KERNEL_ROOT)/stream_buffer.c \
  $(FREERTOS_KERNEL_ROOT)/tasks.c \
  $(FREERTOS_KERNEL_ROOT)/timers.c \
  $(FREERTOS_KERNEL_ROOT)/portable/MemMang/heap_4.c \
  $(SDK_ROOT)/external/freertos/portable/GCC/nrf52/port.c \
  $(SDK_ROOT)/external/freertos/portable/CMSIS/nrf52/port_cmsis.c \
  $(SDK_ROOT)/external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c \
  $(SDK_ROOT)/integration/nrfx/legacy/nrf_drv_clock.c \
  $(SDK_ROOT)/integration/nrfx/legacy/nrf_drv_twi.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_clock.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_gpiote.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_saadc.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_spim.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_twim.c \
  $(SDK_ROOT)/modules/nrfx/drivers/src/nrfx_wdt.c \
  $(CMSIS_FREERTOS_ROOT)/CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c \
  $(CMBACKTRACE_ROOT)/cm_backtrace/cm_backtrace.c \
  $(BMA456_ROOT)/bma4.c \
  $(BMA456_ROOT)/bma456w.c \
  $(LIS2DW12_ROOT)/lis2dw12_reg.c \
  $(ST25DVXXKC_ROOT)/st25dvxxkc.c \
  $(ST25DVXXKC_ROOT)/st25dvxxkc_reg.c \
  $(TINY_AES_ROOT)/aes.c \
  $(FLASHDB_ROOT)/port/fal/src/fal.c \
  $(FLASHDB_ROOT)/port/fal/src/fal_flash.c \
  $(FLASHDB_ROOT)/port/fal/src/fal_partition.c \
  $(OPENR1_SOURCES)

INC_FOLDERS += \
  $(PROJ_DIR)/include \
  $(PROJ_DIR)/platform/nrf52840/sdk \
  $(PROJ_DIR)/platform/nrf52840/sdk/config \
  $(CMSIS_FREERTOS_ROOT)/CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Include \
  $(CMSIS_FREERTOS_ROOT)/CMSIS_5/CMSIS/Core/Include \
  $(CMSIS_FREERTOS_ROOT)/CMSIS_5/CMSIS/RTOS2/Include \
  $(CMBACKTRACE_ROOT)/cm_backtrace \
  $(BMA456_ROOT) \
  $(LIS2DW12_ROOT) \
  $(ST25DVXXKC_ROOT) \
  $(TINY_AES_ROOT) \
  $(PROJ_DIR)/port \
  $(FLASHDB_ROOT)/inc \
  $(FLASHDB_ROOT)/port/fal/inc \
  $(FREERTOS_KERNEL_ROOT)/include \
  $(SDK_ROOT)/external/freertos/portable/GCC/nrf52 \
  $(SDK_ROOT)/external/freertos/portable/CMSIS/nrf52 \
  $(SDK_ROOT)/external/segger_rtt \
  $(SDK_ROOT)/components \
  $(SDK_ROOT)/components/ble/common \
  $(SDK_ROOT)/components/ble/ble_advertising \
  $(SDK_ROOT)/components/ble/peer_manager \
  $(SDK_ROOT)/components/ble/nrf_ble_gatt \
  $(SDK_ROOT)/components/libraries/atomic \
  $(SDK_ROOT)/components/libraries/atomic_flags \
  $(SDK_ROOT)/components/libraries/atomic_fifo \
  $(SDK_ROOT)/components/libraries/delay \
  $(SDK_ROOT)/components/libraries/fds \
  $(SDK_ROOT)/components/libraries/fstorage \
  $(SDK_ROOT)/components/libraries/mutex \
  $(SDK_ROOT)/components/libraries/sortlist \
  $(SDK_ROOT)/components/libraries/timer \
  $(SDK_ROOT)/components/libraries/experimental_section_vars \
  $(SDK_ROOT)/components/libraries/log \
  $(SDK_ROOT)/components/libraries/log/src \
  $(SDK_ROOT)/components/libraries/strerror \
  $(SDK_ROOT)/components/libraries/util \
  $(SDK_ROOT)/components/softdevice/common \
  $(SDK_ROOT)/components/softdevice/s140/headers \
  $(SDK_ROOT)/components/softdevice/s140/headers/nrf52 \
  $(SDK_ROOT)/components/toolchain/cmsis/include \
  $(SDK_ROOT)/integration/nrfx \
  $(SDK_ROOT)/integration/nrfx/legacy \
  $(SDK_ROOT)/modules/nrfx \
  $(SDK_ROOT)/modules/nrfx/drivers/include \
  $(SDK_ROOT)/modules/nrfx/hal \
  $(SDK_ROOT)/modules/nrfx/soc \
  $(SDK_ROOT)/modules/nrfx/mdk

OPT := -Os -g3
CFLAGS += $(OPT) -std=c11
CFLAGS += -DFREERTOS
CFLAGS += -DOPENR1_TOUCH_LAYOUT=$(OPENR1_TOUCH_LAYOUT)
CFLAGS += -DOPENR1_TOUCH_RING_SIZE=$(OPENR1_TOUCH_RING_SIZE)
CFLAGS += -DOPENR1_MOTION_POLICY=$(OPENR1_MOTION_POLICY)
CFLAGS += -DECB=1 -DCBC=0 -DCTR=0
CFLAGS += -DCMB_USER_CFG
CFLAGS += -DFLOAT_ABI_HARD -DNRF52840_XXAA -DNRF_SD_BLE_API_VERSION=7
CFLAGS += -DCONFIG_NFCT_PINS_AS_GPIOS -DCONFIG_GPIO_AS_PINRESET
CFLAGS += -DS140 -DSOFTDEVICE_PRESENT
CFLAGS += -mcpu=cortex-m4 -mthumb -mabi=aapcs
CFLAGS += -mfloat-abi=hard -mfpu=fpv4-sp-d16
CFLAGS += -Wall -Wextra -Wno-unused-parameter -Wno-expansion-to-defined
CFLAGS += -ffunction-sections -fdata-sections
CFLAGS += -fno-strict-aliasing -fno-builtin -fshort-enums -fno-math-errno

ASMFLAGS += -g3 -mcpu=cortex-m4 -mthumb -mabi=aapcs
ASMFLAGS += -mfloat-abi=hard -mfpu=fpv4-sp-d16
ASMFLAGS += -DNRF52840_XXAA -DNRF_SD_BLE_API_VERSION=7 -DS140 -DSOFTDEVICE_PRESENT
ASMFLAGS += -DFREERTOS
ASMFLAGS += -D__HEAP_SIZE=0 -D__STACK_SIZE=8192

LDFLAGS += $(OPT) -mcpu=cortex-m4 -mthumb -mabi=aapcs
LDFLAGS += -mfloat-abi=hard -mfpu=fpv4-sp-d16
LDFLAGS += -L$(SDK_ROOT)/modules/nrfx/mdk -T$(LINKER_SCRIPT)
LDFLAGS += -Wl,--gc-sections,-Map=$(OUTPUT_DIRECTORY)/openr1_nrf52840_s140.map
LDFLAGS += --specs=nano.specs
LIB_FILES += -lc -lnosys -lm

OPENR1_TOUCH_LAYOUT ?= 255
OPENR1_TOUCH_RING_SIZE ?= 0
OPENR1_MOTION_POLICY ?= 1

.PHONY: default
default: openr1_nrf52840_s140

TEMPLATE_PATH := $(SDK_ROOT)/components/toolchain/gcc
include $(TEMPLATE_PATH)/Makefile.common
$(foreach target,$(TARGETS),$(call define_target,$(target)))
