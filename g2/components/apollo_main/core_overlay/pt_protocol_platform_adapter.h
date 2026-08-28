/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_PLATFORM_ADAPTER_H
#define OPEN_CFW_PT_PROTOCOL_PLATFORM_ADAPTER_H

#include <stddef.h>
#include <stdint.h>

#include "pt_protocol_service.h"

enum open_cfw_pt_platform_operation {
    OPEN_CFW_PT_OP_SET_BOX_DETECTED,
    OPEN_CFW_PT_OP_CODEC_DELAY,
    OPEN_CFW_PT_OP_STORE_TERMINAL_MODE,
    OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE,
    OPEN_CFW_PT_OP_POST_INPUT_MESSAGE,
    OPEN_CFW_PT_OP_GET_PRODUCT_MODE,
    OPEN_CFW_PT_OP_SET_PRODUCT_MODE,
    OPEN_CFW_PT_OP_PRODUCTION_RESET,
    OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC,
    OPEN_CFW_PT_OP_WRITE_PSN_14,
    OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36,
    OPEN_CFW_PT_OP_BUZZER_TEST,
    OPEN_CFW_PT_OP_BUZZER_READ,
    OPEN_CFW_PT_OP_BUZZER_WRITE,
    OPEN_CFW_PT_OP_UPDATE_ONBOARDING,
    OPEN_CFW_PT_OP_SET_CHARGER_TEST,
    OPEN_CFW_PT_OP_READ_IDENTIFIER_6,
    OPEN_CFW_PT_OP_READ_SYSTEM_TEXT,
    OPEN_CFW_PT_OP_SET_SYNC_READY,
    OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG,
    OPEN_CFW_PT_OP_READ_PAIR_STATE,
    OPEN_CFW_PT_OP_READ_SESSION_STATUS,
    OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36,
    OPEN_CFW_PT_OP_READ_FONT_VERSION,
    OPEN_CFW_PT_OP_READ_DISPLAY_VALUE,
    OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36,
    OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES,
    OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION,
    OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
    OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER,
    OPEN_CFW_PT_OP_SET_TEST_SCREEN,
    OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS,
    OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG,
    OPEN_CFW_PT_OP_GET_AGING_MODE,
    OPEN_CFW_PT_OP_SET_AGING_MODE,
    OPEN_CFW_PT_OP_SET_BOX_STATE,
    OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7,
    OPEN_CFW_PT_OP_READ_BOX_DETAIL_6,
    OPEN_CFW_PT_OP_WRITE_TIME_21,
    OPEN_CFW_PT_OP_UART_SYNC_TEST,
    OPEN_CFW_PT_OP_CALIBRATE_AMBIENT,
    OPEN_CFW_PT_OP_LENS_SYNC_TEST,
    OPEN_CFW_PT_OP_AUDIO_CONTROL,
    OPEN_CFW_PT_OP_AUDIO_READ_CHUNK,
    OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32,
    OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5,
    OPEN_CFW_PT_OP_OTA_INITIALIZE,
    OPEN_CFW_PT_OP_OTA_DISPATCH,
    OPEN_CFW_PT_OP_OTA_STATUS,
    OPEN_CFW_PT_OP_STORAGE_SELF_TEST,
    OPEN_CFW_PT_OP_READ_METADATA_32,
    OPEN_CFW_PT_OP_STORAGE_READY,
    OPEN_CFW_PT_OP_OPEN_PAYLOAD,
    OPEN_CFW_PT_OP_READ_PAYLOAD_AT,
    OPEN_CFW_PT_OP_CLOSE_PAYLOAD,
    OPEN_CFW_PT_OP_POST_RESPONSE,
    OPEN_CFW_PT_OP_COUNT
};

/*
 * Arguments are native-width scalars or pointers valid for the duration of the
 * call. The board port owns peripheral/persistence behavior and must return a
 * nonzero error when physical evidence or a required service is unavailable.
 */
typedef int (*open_cfw_pt_platform_perform_fn)(
    enum open_cfw_pt_platform_operation operation,
    uintptr_t argument0, uintptr_t argument1,
    uintptr_t argument2, uintptr_t argument3,
    uintptr_t argument4,
    void *context);

struct open_cfw_pt_platform_backend {
    open_cfw_pt_platform_perform_fn perform;
    void *context;
};

struct open_cfw_pt_platform_adapter {
    struct open_cfw_pt_platform_backend backend;
    struct open_cfw_pt_basic_providers basic;
    struct open_cfw_pt_config_providers config;
    struct open_cfw_pt_data_providers data;
    struct open_cfw_pt_display_providers display;
    struct open_cfw_pt_sensor_providers sensors;
    struct open_cfw_pt_service_providers services;
    struct open_cfw_pt_audio_providers audio;
    struct open_cfw_pt_transfer_providers transfer;
    struct open_cfw_pt_all_providers all;
    char text_scratch[256];
};

int open_cfw_pt_platform_adapter_initialize(
    struct open_cfw_pt_platform_adapter *adapter,
    const struct open_cfw_pt_platform_backend *backend);

#endif
