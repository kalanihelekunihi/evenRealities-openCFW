/* SPDX-License-Identifier: MIT */
#include "pt_protocol_platform_adapter.h"


static int perform(struct open_cfw_pt_platform_adapter *adapter,
                   enum open_cfw_pt_platform_operation operation,
                   uintptr_t a0, uintptr_t a1, uintptr_t a2, uintptr_t a3,
                   uintptr_t a4)
{
    if (adapter == NULL || adapter->backend.perform == NULL) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return adapter->backend.perform(operation, a0, a1, a2, a3, a4,
                                    adapter->backend.context);
}

#define ADAPTER(context) ((struct open_cfw_pt_platform_adapter *)(context))
#define CALL0(context, operation) \
    perform(ADAPTER(context), (operation), 0U, 0U, 0U, 0U, 0U)
#define CALL1(context, operation, a0) \
    perform(ADAPTER(context), (operation), (uintptr_t)(a0), 0U, 0U, 0U, 0U)
#define CALL2(context, operation, a0, a1) \
    perform(ADAPTER(context), (operation), (uintptr_t)(a0), (uintptr_t)(a1), \
            0U, 0U, 0U)
#define CALL3(context, operation, a0, a1, a2) \
    perform(ADAPTER(context), (operation), (uintptr_t)(a0), (uintptr_t)(a1), \
            (uintptr_t)(a2), 0U, 0U)
#define CALL4(context, operation, a0, a1, a2, a3) \
    perform(ADAPTER(context), (operation), (uintptr_t)(a0), (uintptr_t)(a1), \
            (uintptr_t)(a2), (uintptr_t)(a3), 0U)
#define CALL5(context, operation, a0, a1, a2, a3, a4) \
    perform(ADAPTER(context), (operation), (uintptr_t)(a0), (uintptr_t)(a1), \
            (uintptr_t)(a2), (uintptr_t)(a3), (uintptr_t)(a4))

static int set_box_detected(int value, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_BOX_DETECTED, value); }
static int codec_delay(void *c) { return CALL0(c, OPEN_CFW_PT_OP_CODEC_DELAY); }
static int store_terminal(uint8_t value, void *c) { return CALL1(c, OPEN_CFW_PT_OP_STORE_TERMINAL_MODE, value); }
static int load_terminal(uint8_t *value, void *c) { return CALL1(c, OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE, value); }
static int post_input(void *c) { return CALL0(c, OPEN_CFW_PT_OP_POST_INPUT_MESSAGE); }
static int get_mode(uint8_t *value, void *c) { return CALL1(c, OPEN_CFW_PT_OP_GET_PRODUCT_MODE, value); }
static int set_mode(uint8_t value, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_PRODUCT_MODE, value); }
static int production_reset(void *c) { return CALL0(c, OPEN_CFW_PT_OP_PRODUCTION_RESET); }
static int touch_diagnostic(uint8_t *p, int16_t *d, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC, p, d); }
static int write_psn(const uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_WRITE_PSN_14, d, n); }
static int write_calibration(const uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36, d, n); }
static int buzzer_test(int e, uint32_t f, uint8_t d, void *c) { return CALL3(c, OPEN_CFW_PT_OP_BUZZER_TEST, e, f, d); }
static int buzzer_read(uint32_t *f, uint8_t *d, void *c) { return CALL2(c, OPEN_CFW_PT_OP_BUZZER_READ, f, d); }
static int buzzer_write(uint32_t f, uint8_t d, void *c) { return CALL2(c, OPEN_CFW_PT_OP_BUZZER_WRITE, f, d); }
static int onboarding(int e, void *c) { return CALL1(c, OPEN_CFW_PT_OP_UPDATE_ONBOARDING, e); }
static int charger_test(int e, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_CHARGER_TEST, e); }
static int read_id(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_IDENTIFIER_6, d, n); }

static int read_text(enum open_cfw_pt_platform_operation op, unsigned int index,
                     const char **text, void *c)
{
    struct open_cfw_pt_platform_adapter *adapter = ADAPTER(c);
    int result;
    if (adapter == NULL || text == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    adapter->text_scratch[0] = '\0';
    result = perform(adapter, op, index, (uintptr_t)adapter->text_scratch,
                     sizeof(adapter->text_scratch), 0U, 0U);
    adapter->text_scratch[sizeof(adapter->text_scratch) - 1U] = '\0';
    if (result == 0) *text = adapter->text_scratch;
    return result;
}
static int system_text(unsigned int i, const char **t, void *c) { return read_text(OPEN_CFW_PT_OP_READ_SYSTEM_TEXT, i, t, c); }
static int font_text(unsigned int i, const char **t, void *c) { return read_text(OPEN_CFW_PT_OP_READ_FONT_VERSION, i, t, c); }
static int sync_ready(int v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_SYNC_READY, v); }
static int read_bool(uint8_t *v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG, v); }
static int read_pair(uint8_t *a, uint8_t *b, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_PAIR_STATE, a, b); }
static int read_session(struct open_cfw_pt_session_status *s, void *c) { return CALL1(c, OPEN_CFW_PT_OP_READ_SESSION_STATUS, s); }
static int read_diag(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36, d, n); }
static int read_display(uint8_t *v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_READ_DISPLAY_VALUE, v); }
static int read_imu(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36, d, n); }
static int touch_differences(int16_t d[5], void *c) { return CALL1(c, OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES, d); }
static int calibration_orientation(int *m, uint8_t o[12], void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION, m, o); }
static int hardware_id(uint8_t s, uint32_t *v, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER, s, v); }
static int platform_id(uint8_t s, uint32_t *v, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER, s, v); }
static int test_screen(uint16_t s, int e, void *c) { return CALL2(c, OPEN_CFW_PT_OP_SET_TEST_SCREEN, s, e); }
static int display_parameters(uint8_t a, uint8_t b, int p, void *c) { return CALL3(c, OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS, a, b, p); }
static int runtime_flag(int e, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG, e); }
static int get_aging(uint8_t *v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_GET_AGING_MODE, v); }
static int set_aging(int e, void *c) { return CALL1(c, OPEN_CFW_PT_OP_SET_AGING_MODE, e); }
static int box_state(uint8_t l, uint8_t ch, int hl, uint8_t lid, void *c) { return CALL4(c, OPEN_CFW_PT_OP_SET_BOX_STATE, l, ch, hl, lid); }
static int box_summary(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7, d, n); }
static int box_detail(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_BOX_DETAIL_6, d, n); }
static int write_time(const uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_WRITE_TIME_21, d, n); }
static int uart_sync(uint8_t *v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_UART_SYNC_TEST, v); }
static int ambient(uint8_t s, uint32_t *m, uint8_t *status, void *c) { return CALL3(c, OPEN_CFW_PT_OP_CALIBRATE_AMBIENT, s, m, status); }
static int lens_sync(uint8_t *v, void *c) { return CALL1(c, OPEN_CFW_PT_OP_LENS_SYNC_TEST, v); }
static int audio_control(uint8_t ch, uint8_t a, uint8_t arg, void *c) { return CALL3(c, OPEN_CFW_PT_OP_AUDIO_CONTROL, ch, a, arg); }
static int audio_chunk(uint8_t s, int r, uint8_t d[210], uint16_t *n, int *done, void *c) { return CALL5(c, OPEN_CFW_PT_OP_AUDIO_READ_CHUNK, s, r, d, n, done); }
static int audio_metrics(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32, d, n); }
static int audio_version(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5, d, n); }
static int ota_initialize(void *c) { return CALL0(c, OPEN_CFW_PT_OP_OTA_INITIALIZE); }
static int ota_dispatch(uint8_t t, const uint8_t *d, size_t n, void *c) { return CALL3(c, OPEN_CFW_PT_OP_OTA_DISPATCH, t, d, n); }
static int ota_status(uint8_t *s, void *c) { return CALL1(c, OPEN_CFW_PT_OP_OTA_STATUS, s); }
static int storage_test(uint8_t *s, void *c) { return CALL1(c, OPEN_CFW_PT_OP_STORAGE_SELF_TEST, s); }
static int metadata(uint8_t *d, size_t n, void *c) { return CALL2(c, OPEN_CFW_PT_OP_READ_METADATA_32, d, n); }
static int storage_ready(uint8_t *s, void *c) { return CALL1(c, OPEN_CFW_PT_OP_STORAGE_READY, s); }
static int open_payload(void *c) { return CALL0(c, OPEN_CFW_PT_OP_OPEN_PAYLOAD); }
static int read_payload(uint32_t o, uint8_t *d, size_t n, size_t *r, void *c) { return CALL4(c, OPEN_CFW_PT_OP_READ_PAYLOAD_AT, o, d, n, r); }
static int close_payload(void *c) { return CALL0(c, OPEN_CFW_PT_OP_CLOSE_PAYLOAD); }

int open_cfw_pt_platform_adapter_initialize(
    struct open_cfw_pt_platform_adapter *a,
    const struct open_cfw_pt_platform_backend *backend)
{
    if (a == NULL || backend == NULL || backend->perform == NULL) {
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    }
    a->backend = *backend;
    a->basic = (struct open_cfw_pt_basic_providers){
        .set_box_detected = set_box_detected, .codec_delay = codec_delay,
        .store_terminal_mode = store_terminal,
        .load_terminal_mode = load_terminal,
        .post_input_message = post_input, .context = a};
    a->config = (struct open_cfw_pt_config_providers){
        .get_product_mode = get_mode, .set_product_mode = set_mode,
        .production_reset_action = production_reset,
        .read_touch_diagnostic = touch_diagnostic,
        .write_and_verify_psn_14 = write_psn,
        .write_sensor_calibration_36 = write_calibration,
        .buzzer_test = buzzer_test, .buzzer_read = buzzer_read,
        .buzzer_write = buzzer_write, .update_onboarding = onboarding,
        .set_charger_test = charger_test, .context = a};
    a->data = (struct open_cfw_pt_data_providers){
        .read_identifier_6 = read_id, .read_system_text = system_text,
        .set_sync_ready = sync_ready, .read_boolean_flag = read_bool,
        .read_pair_state = read_pair, .read_session_status = read_session,
        .read_diagnostic_blob_36 = read_diag,
        .read_font_version = font_text, .read_display_value = read_display,
        .context = a};
    a->display = (struct open_cfw_pt_display_providers){
        .get_product_mode = get_mode, .set_test_screen = test_screen,
        .set_display_parameters = display_parameters,
        .set_runtime_flag = runtime_flag, .get_aging_mode = get_aging,
        .set_aging_mode = set_aging, .context = a};
    a->sensors = (struct open_cfw_pt_sensor_providers){
        .read_latest_imu_sample_36 = read_imu,
        .read_touch_differences = touch_differences,
        .read_calibration_and_orientation = calibration_orientation,
        .read_hardware_identifier = hardware_id,
        .read_platform_identifier = platform_id, .context = a};
    a->services = (struct open_cfw_pt_service_providers){
        .get_product_mode = get_mode, .set_box_state = box_state,
        .read_box_summary_7 = box_summary, .read_box_detail_6 = box_detail,
        .write_and_verify_time_21 = write_time,
        .uart_sync_test = uart_sync, .calibrate_ambient = ambient,
        .lens_sync_test = lens_sync, .context = a};
    a->audio = (struct open_cfw_pt_audio_providers){
        .get_product_mode = get_mode, .control_channel = audio_control,
        .read_test_file_chunk = audio_chunk,
        .read_metrics_32 = audio_metrics,
        .read_version_status_5 = audio_version, .context = a};
    a->transfer = (struct open_cfw_pt_transfer_providers){
        .ota_initialize = ota_initialize, .ota_dispatch = ota_dispatch,
        .ota_status = ota_status, .storage_self_test = storage_test,
        .read_metadata_32 = metadata, .storage_ready = storage_ready,
        .open_payload = open_payload, .read_payload_at = read_payload,
        .close_payload = close_payload, .context = a};
    a->all = (struct open_cfw_pt_all_providers){
        .basic = &a->basic, .config = &a->config, .data = &a->data,
        .display = &a->display, .sensors = &a->sensors,
        .services = &a->services, .audio = &a->audio,
        .transfer = &a->transfer};
    a->text_scratch[0] = '\0';
    return OPEN_CFW_PT_OK;
}
