/* SPDX-License-Identifier: MIT */
#include "pt_protocol_platform_adapter.h"

#include <stdint.h>
#include <string.h>

struct state {
    uint8_t mode;
    uint8_t terminal;
    unsigned int calls;
    int result;
    enum open_cfw_pt_platform_operation operation;
    uintptr_t arguments[5];
};

static int backend(enum open_cfw_pt_platform_operation op,
                   uintptr_t a0, uintptr_t a1, uintptr_t a2, uintptr_t a3,
                   uintptr_t a4, void *context)
{
    struct state *state = context;
    state->operation = op;
    state->arguments[0] = a0;
    state->arguments[1] = a1;
    state->arguments[2] = a2;
    state->arguments[3] = a3;
    state->arguments[4] = a4;
    ++state->calls;
    if (state->result != 0) return state->result;
    switch (op) {
    case OPEN_CFW_PT_OP_SET_PRODUCT_MODE: state->mode = (uint8_t)a0; break;
    case OPEN_CFW_PT_OP_GET_PRODUCT_MODE: *(uint8_t *)a0 = state->mode; break;
    case OPEN_CFW_PT_OP_STORE_TERMINAL_MODE: state->terminal = (uint8_t)a0; break;
    case OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE: *(uint8_t *)a0 = state->terminal; break;
    case OPEN_CFW_PT_OP_READ_IDENTIFIER_6:
        if (a1 != 6U) return -1;
        memcpy((void *)a0, "G2TEST", 6U);
        break;
    case OPEN_CFW_PT_OP_READ_SYSTEM_TEXT:
        if (a2 < 6U) return -1;
        memcpy((void *)a1, a0 == 0U ? "left" : "right", 6U);
        break;
    default: break;
    }
    return 0;
}

#define CHECK(call, expected_operation, e0, e1, e2, e3, e4) do { \
    state.calls = 0U; \
    if ((call) != state.result || state.calls != 1U || \
        state.operation != (expected_operation) || \
        state.arguments[0] != (uintptr_t)(e0) || \
        state.arguments[1] != (uintptr_t)(e1) || \
        state.arguments[2] != (uintptr_t)(e2) || \
        state.arguments[3] != (uintptr_t)(e3) || \
        state.arguments[4] != (uintptr_t)(e4)) return __LINE__; \
} while (0)

int main(void)
{
    struct state state = {0};
    struct open_cfw_pt_platform_backend port = {backend, &state};
    struct open_cfw_pt_platform_adapter adapter;
    struct open_cfw_pt_firmware_service service;
    struct open_cfw_pt_session_status session;
    uint8_t bytes[256] = {0};
    uint8_t transfer_staging[6000] = {0};
    uint8_t value = 0U, other = 0U, status = 0U;
    uint16_t count16 = 0U;
    uint32_t value32 = 0U;
    size_t count = 0U;
    int signed_value = 0;
    int16_t differences[5] = {0};
    const char *text = 0;

    if (open_cfw_pt_platform_adapter_initialize(0, &port) != OPEN_CFW_PT_INVALID_ARGUMENT) return 1;
    if (open_cfw_pt_platform_adapter_initialize(&adapter, 0) != OPEN_CFW_PT_INVALID_ARGUMENT) return 2;
    port.perform = 0;
    if (open_cfw_pt_platform_adapter_initialize(&adapter, &port) != OPEN_CFW_PT_INVALID_ARGUMENT) return 3;
    port.perform = backend;
    if (open_cfw_pt_platform_adapter_initialize(&adapter, &port) != 0) return 4;
    if (open_cfw_pt_firmware_service_initialize(
            &service, &adapter.all, transfer_staging,
            sizeof(transfer_staging)) != 0) return 5;

    CHECK(adapter.basic.set_box_detected(1, adapter.basic.context), OPEN_CFW_PT_OP_SET_BOX_DETECTED, 1, 0, 0, 0, 0);
    CHECK(adapter.basic.codec_delay(adapter.basic.context), OPEN_CFW_PT_OP_CODEC_DELAY, 0, 0, 0, 0, 0);
    CHECK(adapter.basic.store_terminal_mode(9U, adapter.basic.context), OPEN_CFW_PT_OP_STORE_TERMINAL_MODE, 9, 0, 0, 0, 0);
    CHECK(adapter.basic.load_terminal_mode(&value, adapter.basic.context), OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE, &value, 0, 0, 0, 0);
    if (value != 9U) return 6;
    CHECK(adapter.basic.post_input_message(adapter.basic.context), OPEN_CFW_PT_OP_POST_INPUT_MESSAGE, 0, 0, 0, 0, 0);

    CHECK(adapter.config.get_product_mode(&value, adapter.config.context), OPEN_CFW_PT_OP_GET_PRODUCT_MODE, &value, 0, 0, 0, 0);
    CHECK(adapter.config.set_product_mode(3U, adapter.config.context), OPEN_CFW_PT_OP_SET_PRODUCT_MODE, 3, 0, 0, 0, 0);
    CHECK(adapter.config.production_reset_action(adapter.config.context), OPEN_CFW_PT_OP_PRODUCTION_RESET, 0, 0, 0, 0, 0);
    CHECK(adapter.config.read_touch_diagnostic(&value, differences, adapter.config.context), OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC, &value, differences, 0, 0, 0);
    CHECK(adapter.config.write_and_verify_psn_14(bytes, 14U, adapter.config.context), OPEN_CFW_PT_OP_WRITE_PSN_14, bytes, 14, 0, 0, 0);
    CHECK(adapter.config.write_sensor_calibration_36(bytes, 36U, adapter.config.context), OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36, bytes, 36, 0, 0, 0);
    CHECK(adapter.config.buzzer_test(1, 440U, 50U, adapter.config.context), OPEN_CFW_PT_OP_BUZZER_TEST, 1, 440, 50, 0, 0);
    CHECK(adapter.config.buzzer_read(&value32, &value, adapter.config.context), OPEN_CFW_PT_OP_BUZZER_READ, &value32, &value, 0, 0, 0);
    CHECK(adapter.config.buzzer_write(880U, 25U, adapter.config.context), OPEN_CFW_PT_OP_BUZZER_WRITE, 880, 25, 0, 0, 0);
    CHECK(adapter.config.update_onboarding(1, adapter.config.context), OPEN_CFW_PT_OP_UPDATE_ONBOARDING, 1, 0, 0, 0, 0);
    CHECK(adapter.config.set_charger_test(1, adapter.config.context), OPEN_CFW_PT_OP_SET_CHARGER_TEST, 1, 0, 0, 0, 0);

    CHECK(adapter.data.read_identifier_6(bytes, 6U, adapter.data.context), OPEN_CFW_PT_OP_READ_IDENTIFIER_6, bytes, 6, 0, 0, 0);
    if (memcmp(bytes, "G2TEST", 6U) != 0) return 7;
    CHECK(adapter.data.read_system_text(0U, &text, adapter.data.context), OPEN_CFW_PT_OP_READ_SYSTEM_TEXT, 0, adapter.text_scratch, sizeof(adapter.text_scratch), 0, 0);
    if (strcmp(text, "left") != 0) return 8;
    if (adapter.data.read_system_text(0U, &text, 0) != OPEN_CFW_PT_INVALID_ARGUMENT) return 9;
    CHECK(adapter.data.set_sync_ready(1, adapter.data.context), OPEN_CFW_PT_OP_SET_SYNC_READY, 1, 0, 0, 0, 0);
    CHECK(adapter.data.read_boolean_flag(&value, adapter.data.context), OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG, &value, 0, 0, 0, 0);
    CHECK(adapter.data.read_pair_state(&value, &other, adapter.data.context), OPEN_CFW_PT_OP_READ_PAIR_STATE, &value, &other, 0, 0, 0);
    CHECK(adapter.data.read_session_status(&session, adapter.data.context), OPEN_CFW_PT_OP_READ_SESSION_STATUS, &session, 0, 0, 0, 0);
    CHECK(adapter.data.read_diagnostic_blob_36(bytes, 36U, adapter.data.context), OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36, bytes, 36, 0, 0, 0);
    CHECK(adapter.data.read_font_version(1U, &text, adapter.data.context), OPEN_CFW_PT_OP_READ_FONT_VERSION, 1, adapter.text_scratch, sizeof(adapter.text_scratch), 0, 0);
    CHECK(adapter.data.read_display_value(&value, adapter.data.context), OPEN_CFW_PT_OP_READ_DISPLAY_VALUE, &value, 0, 0, 0, 0);

    CHECK(adapter.display.get_product_mode(&value, adapter.display.context), OPEN_CFW_PT_OP_GET_PRODUCT_MODE, &value, 0, 0, 0, 0);
    CHECK(adapter.display.set_test_screen(0x1234U, 1, adapter.display.context), OPEN_CFW_PT_OP_SET_TEST_SCREEN, 0x1234, 1, 0, 0, 0);
    CHECK(adapter.display.set_display_parameters(2U, 3U, 1, adapter.display.context), OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS, 2, 3, 1, 0, 0);
    CHECK(adapter.display.set_runtime_flag(1, adapter.display.context), OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG, 1, 0, 0, 0, 0);
    CHECK(adapter.display.get_aging_mode(&value, adapter.display.context), OPEN_CFW_PT_OP_GET_AGING_MODE, &value, 0, 0, 0, 0);
    CHECK(adapter.display.set_aging_mode(1, adapter.display.context), OPEN_CFW_PT_OP_SET_AGING_MODE, 1, 0, 0, 0, 0);

    CHECK(adapter.sensors.read_latest_imu_sample_36(bytes, 36U, adapter.sensors.context), OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36, bytes, 36, 0, 0, 0);
    CHECK(adapter.sensors.read_touch_differences(differences, adapter.sensors.context), OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES, differences, 0, 0, 0, 0);
    CHECK(adapter.sensors.read_calibration_and_orientation(&signed_value, bytes, adapter.sensors.context), OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION, &signed_value, bytes, 0, 0, 0);
    CHECK(adapter.sensors.read_hardware_identifier(2U, &value32, adapter.sensors.context), OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER, 2, &value32, 0, 0, 0);
    CHECK(adapter.sensors.read_platform_identifier(3U, &value32, adapter.sensors.context), OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER, 3, &value32, 0, 0, 0);

    CHECK(adapter.services.get_product_mode(&value, adapter.services.context), OPEN_CFW_PT_OP_GET_PRODUCT_MODE, &value, 0, 0, 0, 0);
    CHECK(adapter.services.set_box_state(4U, 1U, 1, 5U, adapter.services.context), OPEN_CFW_PT_OP_SET_BOX_STATE, 4, 1, 1, 5, 0);
    CHECK(adapter.services.read_box_summary_7(bytes, 7U, adapter.services.context), OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7, bytes, 7, 0, 0, 0);
    CHECK(adapter.services.read_box_detail_6(bytes, 6U, adapter.services.context), OPEN_CFW_PT_OP_READ_BOX_DETAIL_6, bytes, 6, 0, 0, 0);
    CHECK(adapter.services.write_and_verify_time_21(bytes, 21U, adapter.services.context), OPEN_CFW_PT_OP_WRITE_TIME_21, bytes, 21, 0, 0, 0);
    CHECK(adapter.services.uart_sync_test(&value, adapter.services.context), OPEN_CFW_PT_OP_UART_SYNC_TEST, &value, 0, 0, 0, 0);
    CHECK(adapter.services.calibrate_ambient(2U, &value32, &status, adapter.services.context), OPEN_CFW_PT_OP_CALIBRATE_AMBIENT, 2, &value32, &status, 0, 0);
    CHECK(adapter.services.lens_sync_test(&value, adapter.services.context), OPEN_CFW_PT_OP_LENS_SYNC_TEST, &value, 0, 0, 0, 0);

    CHECK(adapter.audio.get_product_mode(&value, adapter.audio.context), OPEN_CFW_PT_OP_GET_PRODUCT_MODE, &value, 0, 0, 0, 0);
    CHECK(adapter.audio.control_channel(2U, 3U, 4U, adapter.audio.context), OPEN_CFW_PT_OP_AUDIO_CONTROL, 2, 3, 4, 0, 0);
    CHECK(adapter.audio.read_test_file_chunk(5U, 1, bytes, &count16, &signed_value, adapter.audio.context), OPEN_CFW_PT_OP_AUDIO_READ_CHUNK, 5, 1, bytes, &count16, &signed_value);
    CHECK(adapter.audio.read_metrics_32(bytes, 32U, adapter.audio.context), OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32, bytes, 32, 0, 0, 0);
    CHECK(adapter.audio.read_version_status_5(bytes, 5U, adapter.audio.context), OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5, bytes, 5, 0, 0, 0);

    CHECK(adapter.transfer.ota_initialize(adapter.transfer.context), OPEN_CFW_PT_OP_OTA_INITIALIZE, 0, 0, 0, 0, 0);
    CHECK(adapter.transfer.ota_dispatch(2U, bytes, 12U, adapter.transfer.context), OPEN_CFW_PT_OP_OTA_DISPATCH, 2, bytes, 12, 0, 0);
    CHECK(adapter.transfer.ota_status(&status, adapter.transfer.context), OPEN_CFW_PT_OP_OTA_STATUS, &status, 0, 0, 0, 0);
    CHECK(adapter.transfer.storage_self_test(&status, adapter.transfer.context), OPEN_CFW_PT_OP_STORAGE_SELF_TEST, &status, 0, 0, 0, 0);
    CHECK(adapter.transfer.read_metadata_32(bytes, 32U, adapter.transfer.context), OPEN_CFW_PT_OP_READ_METADATA_32, bytes, 32, 0, 0, 0);
    CHECK(adapter.transfer.storage_ready(&status, adapter.transfer.context), OPEN_CFW_PT_OP_STORAGE_READY, &status, 0, 0, 0, 0);
    CHECK(adapter.transfer.open_payload(adapter.transfer.context), OPEN_CFW_PT_OP_OPEN_PAYLOAD, 0, 0, 0, 0, 0);
    CHECK(adapter.transfer.read_payload_at(1234U, bytes, 99U, &count, adapter.transfer.context), OPEN_CFW_PT_OP_READ_PAYLOAD_AT, 1234, bytes, 99, &count, 0);
    CHECK(adapter.transfer.close_payload(adapter.transfer.context), OPEN_CFW_PT_OP_CLOSE_PAYLOAD, 0, 0, 0, 0, 0);

    state.result = -23;
    CHECK(adapter.basic.codec_delay(adapter.basic.context), OPEN_CFW_PT_OP_CODEC_DELAY, 0, 0, 0, 0, 0);
    return 0;
}
