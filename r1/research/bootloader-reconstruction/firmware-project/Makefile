PROJECT_NAME := r1_secure_bootloader
TARGETS := r1_bootloader

PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
SDK_ROOT := $(PROJECT_ROOT)/vendor/nrf5-sdk
PROFILE ?= captured
GNU_INSTALL_ROOT ?=
GNU_PREFIX ?= arm-none-eabi
LIVE_IMAGE ?=
export SOURCE_DATE_EPOCH := 1629676800

ifeq ($(filter $(PROFILE),captured hardened transition),)
$(error PROFILE must be captured, hardened, or transition)
endif

ifeq ($(PROFILE),transition)
ifeq ($(strip $(TRANSITION_IMAGE_BYTES)),)
$(error TRANSITION_IMAGE_BYTES is required for PROFILE=transition)
endif
ifeq ($(strip $(TRANSITION_IMAGE_CRC32)),)
$(error TRANSITION_IMAGE_CRC32 is required for PROFILE=transition)
endif
PROJECT_PUBLIC_KEY := $(PROJECT_ROOT)/src/r1_transition_public_key.c
PROJECT_MAIN := $(PROJECT_ROOT)/src/r1_transition_main.c
else
PROJECT_PUBLIC_KEY := $(PROJECT_ROOT)/src/r1_dfu_public_key.c
PROJECT_MAIN := $(SDK_ROOT)/examples/dfu/secure_bootloader/main.c
endif

OUTPUT_DIRECTORY := build/$(PROFILE)
LINKER_SCRIPT := $(SDK_ROOT)/examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc/secure_bootloader_gcc_nrf52.ld

$(OUTPUT_DIRECTORY)/r1_bootloader.out: LINKER_SCRIPT := $(LINKER_SCRIPT)

SRC_FILES += \
  $(SDK_ROOT)/modules/nrfx/mdk/gcc_startup_nrf52840.S \
  $(SDK_ROOT)/components/libraries/log/src/nrf_log_frontend.c \
  $(SDK_ROOT)/components/libraries/log/src/nrf_log_str_formatter.c \
  $(SDK_ROOT)/components/libraries/util/app_error_weak.c \
  $(SDK_ROOT)/components/libraries/scheduler/app_scheduler.c \
  $(SDK_ROOT)/components/libraries/util/app_util_platform.c \
  $(SDK_ROOT)/components/libraries/crc32/crc32.c \
  $(SDK_ROOT)/components/libraries/mem_manager/mem_manager.c \
  $(SDK_ROOT)/components/libraries/util/nrf_assert.c \
  $(SDK_ROOT)/components/libraries/atomic_fifo/nrf_atfifo.c \
  $(SDK_ROOT)/components/libraries/atomic/nrf_atomic.c \
  $(SDK_ROOT)/components/libraries/balloc/nrf_balloc.c \
  $(SDK_ROOT)/external/fprintf/nrf_fprintf.c \
  $(SDK_ROOT)/external/fprintf/nrf_fprintf_format.c \
  $(SDK_ROOT)/components/libraries/fstorage/nrf_fstorage.c \
  $(SDK_ROOT)/components/libraries/fstorage/nrf_fstorage_nvmc.c \
  $(SDK_ROOT)/components/libraries/fstorage/nrf_fstorage_sd.c \
  $(SDK_ROOT)/components/libraries/memobj/nrf_memobj.c \
  $(SDK_ROOT)/components/libraries/queue/nrf_queue.c \
  $(SDK_ROOT)/components/libraries/ringbuf/nrf_ringbuf.c \
  $(SDK_ROOT)/components/libraries/experimental_section_vars/nrf_section_iter.c \
  $(SDK_ROOT)/components/libraries/strerror/nrf_strerror.c \
  $(SDK_ROOT)/modules/nrfx/mdk/system_nrf52840.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_ecc.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_ecdsa.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_hash.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_init.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_shared.c \
  $(SDK_ROOT)/components/boards/boards.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh_ble.c \
  $(SDK_ROOT)/components/softdevice/common/nrf_sdh_soc.c \
  $(SDK_ROOT)/modules/nrfx/hal/nrf_nvmc.c \
  $(SDK_ROOT)/modules/nrfx/soc/nrfx_atomic.c \
  $(SDK_ROOT)/components/libraries/crypto/nrf_crypto_ecc.c \
  $(SDK_ROOT)/components/libraries/crypto/nrf_crypto_ecdsa.c \
  $(SDK_ROOT)/components/libraries/crypto/nrf_crypto_hash.c \
  $(SDK_ROOT)/components/libraries/crypto/nrf_crypto_init.c \
  $(SDK_ROOT)/components/libraries/crypto/nrf_crypto_shared.c \
  $(PROJECT_PUBLIC_KEY) \
  $(PROJECT_MAIN) \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_svci.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_svci_handler.c \
  $(SDK_ROOT)/components/libraries/svc/nrf_svc_handler.c \
  $(SDK_ROOT)/components/ble/common/ble_srv_common.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_app_start.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_app_start_final.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_dfu_timers.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_fw_activation.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_info.c \
  $(SDK_ROOT)/components/libraries/bootloader/nrf_bootloader_wdt.c \
  $(SDK_ROOT)/external/nano-pb/pb_common.c \
  $(SDK_ROOT)/external/nano-pb/pb_decode.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/dfu-cc.pb.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu.c \
  $(SDK_ROOT)/components/libraries/bootloader/ble_dfu/nrf_dfu_ble.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_flash.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_handling_error.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_mbr.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_req_handler.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_settings.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_settings_svci.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_transport.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_utils.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_validation.c \
  $(SDK_ROOT)/components/libraries/bootloader/dfu/nrf_dfu_ver_validation.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_chacha_poly_aead.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_ecc.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_ecdh.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_ecdsa.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_eddsa.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_hash.c \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon/oberon_backend_hmac.c

INC_FOLDERS += \
  $(SDK_ROOT)/components/libraries/crypto/backend/micro_ecc \
  $(SDK_ROOT)/components/libraries/memobj \
  $(SDK_ROOT)/components/softdevice/s140/headers/nrf52 \
  $(SDK_ROOT)/components/libraries/crc32 \
  $(SDK_ROOT)/components/libraries/experimental_section_vars \
  $(SDK_ROOT)/components/libraries/mem_manager \
  $(SDK_ROOT)/components/libraries/fstorage \
  $(SDK_ROOT)/components/libraries/util \
  $(SDK_ROOT)/modules/nrfx \
  $(SDK_ROOT)/components/libraries/crypto/backend/oberon \
  $(SDK_ROOT)/components/libraries/crypto/backend/cifra \
  $(SDK_ROOT)/components/libraries/atomic \
  $(SDK_ROOT)/integration/nrfx \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310_bl \
  $(SDK_ROOT)/external/nrf_cc310/include \
  $(SDK_ROOT)/components/libraries/log/src \
  $(SDK_ROOT)/components/libraries/bootloader/dfu \
  $(SDK_ROOT)/components/ble/common \
  $(SDK_ROOT)/components/libraries/delay \
  $(SDK_ROOT)/components/libraries/svc \
  $(SDK_ROOT)/components/libraries/crypto/backend/nrf_hw \
  $(SDK_ROOT)/components/libraries/log \
  $(SDK_ROOT)/external/nrf_oberon \
  $(SDK_ROOT)/components/libraries/strerror \
  $(SDK_ROOT)/components/libraries/crypto/backend/mbedtls \
  $(SDK_ROOT)/components/boards \
  $(SDK_ROOT)/components/libraries/crypto/backend/cc310 \
  $(SDK_ROOT)/components/libraries/bootloader \
  $(SDK_ROOT)/components/softdevice/s140/headers \
  $(SDK_ROOT)/components/libraries/crypto \
  $(SDK_ROOT)/examples/dfu/secure_bootloader/pca10056_s140_ble/config \
  $(SDK_ROOT)/components/libraries/crypto/backend/optiga \
  $(SDK_ROOT)/components/libraries/scheduler \
  $(SDK_ROOT)/external/nrf_cc310_bl/include \
  $(SDK_ROOT)/modules/nrfx/hal \
  $(SDK_ROOT)/external/fprintf \
  $(SDK_ROOT)/components/toolchain/cmsis/include \
  $(SDK_ROOT)/components/libraries/balloc \
  $(SDK_ROOT)/components/libraries/atomic_fifo \
  $(SDK_ROOT)/examples/dfu/secure_bootloader \
  $(SDK_ROOT)/components/libraries/crypto/backend/nrf_sw \
  $(SDK_ROOT)/modules/nrfx/mdk \
  $(SDK_ROOT)/components/libraries/bootloader/ble_dfu \
  $(SDK_ROOT)/components/softdevice/common \
  $(SDK_ROOT)/external/nano-pb \
  $(SDK_ROOT)/components/libraries/queue \
  $(SDK_ROOT)/components/libraries/mutex \
  $(SDK_ROOT)/components/libraries/ringbuf

LIB_FILES += \
  $(SDK_ROOT)/external/nrf_oberon/lib/cortex-m4/hard-float/liboberon_3.0.8.a \
  $(SDK_ROOT)/external/nrf_cc310_bl/lib/cortex-m4/hard-float/libnrf_cc310_bl_0.9.13.a \
  -lc -lnosys -lm

OPT := -Os -g3
CFLAGS += $(OPT)
CFLAGS += -DBLE_STACK_SUPPORT_REQD -DBOARD_PCA10056 -DCONFIG_GPIO_AS_PINRESET
CFLAGS += -DFLOAT_ABI_HARD -DNRF52840_XXAA -DNRF_DFU_SETTINGS_VERSION=2
CFLAGS += -DNRF_DFU_SVCI_ENABLED -DNRF_SD_BLE_API_VERSION=7 -DS140
CFLAGS += -DSOFTDEVICE_PRESENT -DSVC_INTERFACE_CALL_AS_NORMAL_FUNCTION
CFLAGS += -D__HEAP_SIZE=0
CFLAGS += -include $(PROJECT_ROOT)/config/r1_recovered_config.h
ifeq ($(PROFILE),captured)
CFLAGS += -DR1_BUILD_PROFILE_CAPTURED=1
else
CFLAGS += -DR1_BUILD_PROFILE_CAPTURED=0
endif
ifeq ($(PROFILE),transition)
CFLAGS += -DR1_BUILD_PROFILE_TRANSITION=1
CFLAGS += -DR1_TRANSITION_IMAGE_BYTES=$(TRANSITION_IMAGE_BYTES)
CFLAGS += -DR1_TRANSITION_IMAGE_CRC32=$(TRANSITION_IMAGE_CRC32)
endif
CFLAGS += -mcpu=cortex-m4 -mthumb -mabi=aapcs
CFLAGS += -Wall -Werror -mfloat-abi=hard -mfpu=fpv4-sp-d16
CFLAGS += -ffunction-sections -fdata-sections -fno-strict-aliasing
CFLAGS += -fno-builtin -fshort-enums
CFLAGS += -ffile-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
CFLAGS += -fdebug-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
CFLAGS += -fmacro-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
ifneq ($(strip $(GNU_INSTALL_ROOT)),)
TOOLCHAIN_ROOT_REAL := $(realpath $(GNU_INSTALL_ROOT)/..)
CFLAGS += -ffile-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
CFLAGS += -fdebug-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
CFLAGS += -fmacro-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
endif

ASMFLAGS += -g3 -mcpu=cortex-m4 -mthumb -mabi=aapcs
ASMFLAGS += -mfloat-abi=hard -mfpu=fpv4-sp-d16
ASMFLAGS += -DBLE_STACK_SUPPORT_REQD -DBOARD_PCA10056 -DCONFIG_GPIO_AS_PINRESET
ASMFLAGS += -DFLOAT_ABI_HARD -DNRF52840_XXAA -DNRF_DFU_SETTINGS_VERSION=2
ASMFLAGS += -DNRF_DFU_SVCI_ENABLED -DNRF_SD_BLE_API_VERSION=7 -DS140
ASMFLAGS += -DSOFTDEVICE_PRESENT -DSVC_INTERFACE_CALL_AS_NORMAL_FUNCTION -D__HEAP_SIZE=0
ASMFLAGS += -ffile-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
ASMFLAGS += -fdebug-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
ASMFLAGS += -fmacro-prefix-map=$(PROJECT_ROOT)=/r1-firmware-project
ifneq ($(strip $(GNU_INSTALL_ROOT)),)
ASMFLAGS += -ffile-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
ASMFLAGS += -fdebug-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
ASMFLAGS += -fmacro-prefix-map=$(TOOLCHAIN_ROOT_REAL)=/arm-toolchain
endif

LDFLAGS += $(OPT) -mthumb -mabi=aapcs
LDFLAGS += -L$(SDK_ROOT)/modules/nrfx/mdk -T$(LINKER_SCRIPT)
LDFLAGS += -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16
LDFLAGS += -Wl,--gc-sections --specs=nano.specs

.PHONY: default verify vendor-verify test model-test
default: r1_bootloader

build:
	mkdir -p $@

$(OUTPUT_DIRECTORY): | build

TEMPLATE_PATH := $(SDK_ROOT)/components/toolchain/gcc
include $(TEMPLATE_PATH)/Makefile.common
$(foreach target,$(TARGETS),$(call define_target,$(target)))

# Nordic's generic binary rule includes the distant UICR load addresses and
# creates a roughly 255 MiB sparse-looking file. Emit the useful 0xf8000-fe000
# bootloader region instead, padded with erased flash bytes to exactly 0x6000.
$(OUTPUT_DIRECTORY)/r1_bootloader.bin: $(OUTPUT_DIRECTORY)/r1_bootloader.out
	$(OBJCOPY) -O binary --gap-fill=0xff --pad-to=0x000fe000 \
	  --remove-section=.uicr_bootloader_start_address \
	  --remove-section=.uicr_mbr_params_page \
	  --remove-section=.bootloader_settings_page \
	  --remove-section=.mbr_params_page $< $@

verify: r1_bootloader
	python3 tools/verify_project.py --profile $(PROFILE) \
	  --tool-prefix $(GNU_INSTALL_ROOT)$(GNU_PREFIX)- $(if $(LIVE_IMAGE),--live-image $(LIVE_IMAGE))

vendor-verify:
	python3 tools/vendor_sdk_subset.py --verify-only

model-test:
	$(MAKE) -C ../functional-model clean test
	$(MAKE) -C ../functional-model clean

test: vendor-verify
	$(MAKE) verify PROFILE=captured GNU_INSTALL_ROOT=$(GNU_INSTALL_ROOT)
	$(MAKE) verify PROFILE=hardened GNU_INSTALL_ROOT=$(GNU_INSTALL_ROOT)
	$(MAKE) model-test
