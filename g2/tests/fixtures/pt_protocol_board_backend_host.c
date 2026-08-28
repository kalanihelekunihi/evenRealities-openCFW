/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <string.h>

#include "pt_protocol_board_backend.h"

static uint8_t local_lid;
static uint8_t local_level;
static uint8_t local_charging;
static uint8_t system_data[16];
static char product_serial[15];
static uint8_t product_mode;
static uint32_t buzzer_frequency;
static uint8_t buzzer_duty;
static uint8_t onboarding;
static unsigned int input_posts;
static unsigned int calibration_updates;
static unsigned int reset_actions;
static uint8_t charger_test;
static uint8_t identifier_record[7] = {
    0xFFU, 1U, 2U, 3U, 4U, 5U, 6U
};
static const uint8_t *identifier_link = identifier_record;
static volatile uint8_t sync_ready;
static uint8_t boolean_flag = 3U;
static uint8_t pair_state[0x2EU];
static uint8_t session_record[0xACU];
static uint8_t diagnostic_blob[36];
static uint8_t display_value = 0x71U;
static volatile uint8_t display_runtime_flag;
static uint8_t aging_mode = 1U;
static float imu_sample[9] = {1.0F, 2.0F, 3.0F, 4.0F, 5.0F};
static float reference_matrix[9] = {
    1.0F, 0.0F, 0.0F, 0.0F, 1.0F, 0.0F, 0.0F, 0.0F, 1.0F
};
static float orientation[3] = {0.25F, -0.5F, 0.75F};
static char board_serial[22] = "BOARD-TEXT";
static uint32_t touch_platform_id = 0x01020304U;
static uint32_t apollo_platform_id = 0x11223344U;
static uint8_t fake_file_data[300];
static unsigned int fake_file_position;
static uint8_t fake_file_opened;
static uint32_t metadata_word;
static void *payload_handle_slot;
static uint8_t payload_active;
static uint32_t payload_open_seconds;
static const char payload_path[] = "/firmware/box.bin";
static const char file_read_mode[] = "r";
static const char file_write_mode[] = "w";
static const char storage_test_path[] = "boot_count";
static const char *const storage_required_paths[4] = {
    "/firmware/ble_em9305.bin", "/firmware/box.bin",
    "/firmware/codec.bin", "/firmware/touch.bin"
};
static const char *const cleanup_paths[3] = {
    "ota/s200_firmware_ota.bin", "audio/rear_mic_00.pcm",
    "audio/front_mic_00.pcm"
};
static unsigned int cleanup_removals;
static uint32_t ota_interface;
static uint8_t ota_frame[129];
static uint16_t ota_frame_length;
static uint8_t ota_frame_command;
static int ota_priority;
static uint8_t ota_stock_sequence;
static uint8_t ota_stock_initialized;
static uint32_t ota_stock_staging_length;
static uint8_t ota_async_data[6000];
static uint32_t ota_async_length;
static uint8_t ota_async_ready;
static uint8_t ota_status = 7U;
static uint8_t uart_sync_state[8];
static const uint8_t uart_sync_expected[7] = {
    0x10U, 0x20U, 0x30U, 0x40U, 0x50U, 0x60U, 0x70U
};
static uint8_t lens_sync_ready;
static uint8_t lens_sync_template[12] = {
    1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U, 9U, 10U, 11U, 12U
};
static uint8_t lens_sync_payload[12];
static uint8_t display_active;
static uint16_t last_screen_id;
static uint32_t last_brightness_delay;
static uint32_t last_brightness_value;
static uint32_t display_stage_mask;
static uint8_t display_offset_first;
static uint8_t display_offset_second;
static uint8_t audio_status = 0xA5U;
static const char firmware_version[] = "2.2.6.10";
static uint8_t audio_action;
static uint8_t audio_argument;
static uint32_t audio_route_channel;
static uint8_t audio_template_0[12] = {0x10U};
static uint8_t audio_template_1[12] = {0x20U};
static void *audio_handle_slot;
static uint8_t audio_active;
static uint32_t audio_length_state;
static uint32_t audio_offset_state;
static uint8_t audio_path_state[32];
static unsigned int aging_resets;
static uint32_t configured_time_value;
static int configured_timezone;
static uint8_t time_configuration[9] = {
    0U, 0U, 0U, 0U, 0x78U, 0x56U, 0x34U, 0x12U, 0xFBU
};
static uint32_t ambient_baseline;
static uint32_t ambient_secondary;
static unsigned int system_resets;
static unsigned int box_state_updates;
static unsigned int display_postprocesses;

static void set_lid(uint8_t value) { local_lid = value; }
static void set_level(uint8_t value) { local_level = value; }
static void set_charging(uint8_t value) { local_charging = value; }
static int32_t codec_delay(void) { return 0; }
static int system_write(uint8_t index, const void *data)
{
    if (data == NULL) return -1;
    if (index == 0U) memcpy(product_serial, data, 15U);
    else if (index == 1U) {
        memcpy(board_serial, data, 21U);
        board_serial[21] = '\0';
    }
    else system_data[index] = *(const uint8_t *)data;
    return 0;
}
static void *system_get(uint8_t index)
{
    if (index == 0U) return (void *)product_serial;
    if (index == 1U) return (void *)board_serial;
    return (void *)&system_data[index];
}
static void *system_read(uint8_t index) { return system_get(index); }
static void post_input(void) { ++input_posts; }
static uint8_t mode_read(void) { return product_mode; }
static void mode_update(uint8_t mode) { product_mode = mode; }
static uint8_t proximity(void) { return 0x5AU; }
static int32_t differences(uint8_t data[10])
{
    unsigned int index;
    for (index = 0U; index < 10U; ++index) data[index] = 0U;
    data[8] = 0x34U;
    data[9] = 0xF2U;
    return 0;
}
static int write_otp(const char *serial)
{
    return serial != NULL && serial[14] == '\0' ? 0 : -1;
}
static int compare(const void *left, const void *right, unsigned int length)
{
    return memcmp(left, right, length);
}
static void calibration(const float *a, const float *b, const float matrix[9])
{
    (void)a;
    (void)b;
    if (matrix != NULL) ++calibration_updates;
}
static void buzzer_start(uint32_t frequency, uint8_t duty)
{
    buzzer_frequency = frequency;
    buzzer_duty = duty;
}
static void buzzer_stop(void) { buzzer_frequency = 0U; buzzer_duty = 0U; }
static uint32_t buzzer_frequency_get(void) { return buzzer_frequency; }
static uint8_t buzzer_duty_get(void) { return buzzer_duty; }
static void buzzer_update(uint32_t frequency, uint8_t duty)
{
    buzzer_frequency = frequency;
    buzzer_duty = duty;
}
static int onboarding_update(uint8_t index, const uint8_t *value)
{
    if (index != 0U || value == NULL) return -1;
    onboarding = *value;
    return 0;
}
static void production_reset(void) { ++reset_actions; }
static void charger_disable(void) { charger_test = 0U; }
static void charger_enable(void) { charger_test = 1U; }
static const char *font_version(void) { return "1.2.3"; }
static const float *latest_imu(void) { return imu_sample; }
static void calibration_initialize(void) {}
static int calibration_read(float a[3], float b[3], float matrix[9])
{
    memcpy(matrix, reference_matrix, sizeof(reference_matrix));
    memset(a, 0, 3U * sizeof(float));
    memset(b, 0, 3U * sizeof(float));
    return 0;
}
static const float *orientation_read(void) { return orientation; }
static uint32_t codec_platform_id(void) { return 0x55667788U; }
static void *file_open(const void *path, const char *mode)
{
    unsigned int index;
    int known = strcmp(path, payload_path) == 0 ||
        strcmp(path, storage_test_path) == 0;
    for (index = 0U; index < 4U; ++index)
        if (strcmp(path, storage_required_paths[index]) == 0) known = 1;
    for (index = 0U; index < 3U; ++index)
        if (strcmp(path, cleanup_paths[index]) == 0) known = 1;
    if (!known || (strcmp(mode, file_read_mode) != 0 &&
            strcmp(mode, file_write_mode) != 0)) return NULL;
    fake_file_position = 0U;
    fake_file_opened = 1U;
    return fake_file_data;
}
static unsigned int file_write(const void *source, unsigned int element_size,
                               unsigned int element_count, void *file)
{
    unsigned int wanted;
    if (file != fake_file_data || fake_file_opened == 0U ||
        element_size != 1U || source == NULL) return 0U;
    wanted = element_count;
    if (wanted > sizeof(fake_file_data) - fake_file_position)
        wanted = (unsigned int)sizeof(fake_file_data) - fake_file_position;
    memcpy(fake_file_data + fake_file_position, source, wanted);
    fake_file_position += wanted;
    return wanted;
}
static int file_close(void *file)
{
    if (file != fake_file_data || fake_file_opened == 0U) return -1;
    fake_file_opened = 0U;
    return 0;
}
static unsigned int file_read(void *destination, unsigned int element_size,
                              unsigned int element_count, void *file)
{
    unsigned int wanted;
    if (file != fake_file_data || fake_file_opened == 0U ||
        element_size != 1U || destination == NULL) return 0U;
    wanted = element_count;
    if (wanted > sizeof(fake_file_data) - fake_file_position)
        wanted = (unsigned int)sizeof(fake_file_data) - fake_file_position;
    memcpy(destination, fake_file_data + fake_file_position, wanted);
    fake_file_position += wanted;
    return wanted;
}
static int file_seek(void *file, int offset, unsigned int origin)
{
    if (file != fake_file_data || fake_file_opened == 0U || origin != 0U ||
        offset < 0 || (unsigned int)offset > sizeof(fake_file_data)) return -1;
    fake_file_position = (unsigned int)offset;
    return 0;
}
static int file_tell(void *file)
{
    return file == fake_file_data && fake_file_opened != 0U ?
        (int)fake_file_position : -1;
}
static int file_size(void *file)
{ return file == fake_file_data && fake_file_opened != 0U ? 300 : -1; }
static int file_remove(const void *path)
{
    unsigned int index;
    for (index = 0U; index < 3U; ++index) {
        if (strcmp(path, cleanup_paths[index]) == 0) {
            cleanup_removals |= 1U << index;
            return 0;
        }
    }
    return -1;
}
static uint32_t tick_count(void) { return 123456U; }
static void ota_set_interface(uint32_t interface, uint32_t service,
                              void *callback, uint32_t enabled)
{
    (void)service;
    (void)callback;
    (void)enabled;
    ota_interface = interface;
}
static int ota_frame_dispatch(uint8_t command, const uint8_t *payload,
                              uint16_t length)
{
    if (payload == NULL || length > sizeof(ota_frame)) return -1;
    ota_frame_command = command;
    ota_frame_length = length;
    memcpy(ota_frame, payload, length);
    return 0;
}
static void *thread_get_id(void) { return ota_frame; }
static int thread_set_priority(void *thread, int priority)
{
    if (thread != ota_frame) return -1;
    ota_priority = priority;
    return 0;
}
static int hardware_id_0(uint32_t *value) { *value = 0xAABBCCDDU; return 0; }
static int hardware_id_1(uint32_t *value) { *value = 0x11223344U; return 0; }
static int hardware_id_2(uint32_t *value) { *value = 0x00000123U; return 0; }
static int imu_who_am_i(uint32_t *value) { *value = 0x01020304U; return 0; }
static int mag_who_am_i(uint32_t *value) { *value = 0x05060708U; return 0; }
static uint32_t display_hardware_id(void) { return 0x1234ABCDU; }
static void ambient_id_initialize(void) {}
static void ambient_id_assign(void *device) { memset(device, 0, 60U); }
static void ambient_id_step_1(void *device) { ((uint8_t *)device)[0] = 1U; }
static void ambient_id_step_2(void *device) { ((uint8_t *)device)[1] = 2U; }
static uint16_t ambient_id_low(void *device)
{ return ((uint8_t *)device)[0] == 1U ? 0x1234U : 0U; }
static uint16_t ambient_id_high(void *device)
{ return ((uint8_t *)device)[1] == 2U ? 0xABCDU : 0U; }
static int uart_sync_write(const uint8_t *data, uint32_t length,
                           uint32_t timeout)
{
    (void)timeout;
    if (data == NULL || length != 7U) return -1;
    memcpy(uart_sync_state + 1U, data, 7U);
    uart_sync_state[0] = 0U;
    return 0;
}
static int delay_ticks(uint32_t ticks)
{
    return ticks == 1U || ticks == 20U || ticks == 1000U ||
        ticks == 2000U ? 0 : -1;
}
static void system_reset(void) { ++system_resets; }
static void box_state_updated(void) { ++box_state_updates; }
static void display_postprocess(void) { ++display_postprocesses; }
static uint8_t font_crc_check_0(void) { return 1U; }
static uint8_t font_crc_check_1(void) { return 2U; }
static uint8_t lens_side(void) { return 1U; }
static int lens_sync_send(uint32_t service, const void *payload,
                          uint32_t length, uint32_t reserved)
{
    (void)reserved;
    if (service != 0x102U || payload == NULL || length != 12U) return -1;
    memcpy(lens_sync_payload, payload, 12U);
    lens_sync_ready = 1U;
    return 0;
}
static void screen_show(uint16_t id, uint32_t a1, uint32_t a2)
{ (void)a1; (void)a2; last_screen_id = id; display_active = 1U; }
static void screen_hide(uint16_t id, uint32_t a1, uint32_t a2)
{ (void)a1; (void)a2; last_screen_id = id; display_active = 0U; }
static const uint8_t *display_state(void) { return &display_active; }
static void display_brightness(uint32_t delay, uint32_t period,
                               uint32_t brightness)
{ (void)period; last_brightness_delay = delay; last_brightness_value = brightness; }
static void display_stage_1(uint32_t value)
{ if (value == 0x60U) display_stage_mask |= 1U; }
static void display_stage_2(uint32_t first, uint32_t second)
{ if (first == 0U && second == 0U) display_stage_mask |= 2U; }
static void display_stage_3(uint32_t value)
{ if (value == 0x20U) display_stage_mask |= 4U; }
static void display_offset(uint8_t first, uint8_t second)
{ display_offset_first = first; display_offset_second = second; }
static const uint8_t *audio_status_get(uint32_t index)
{ return index == 1U ? &audio_status : NULL; }
static void audio_path_format(uint8_t selector, char *path, uint32_t capacity)
{
    (void)selector;
    if (path == NULL || capacity == 0U) return;
    strncpy(path, payload_path, capacity - 1U);
    path[capacity - 1U] = '\0';
}
static void audio_channel_0_start(uint8_t argument)
{ audio_action = 1U; audio_argument = argument; }
static void audio_channel_0_stop(void) { audio_action = 2U; }
static void audio_channel_1_start(void) { audio_action = 3U; }
static void audio_channel_1_stop(void) { audio_action = 4U; }
static void audio_codec_route(uint32_t code, uint32_t channel_0)
{ if (code == 0x86U) audio_route_channel = channel_0; }
static void system_data_reset_aging(void) { ++aging_resets; }
static void time_configure(uint32_t value, int timezone)
{ configured_time_value = value; configured_timezone = timezone; }
static void time_capture(void *record)
{
    unsigned int index;
    for (index = 0U; index < 40U; ++index)
        ((uint8_t *)record)[index] = (uint8_t)(index + 1U);
}
static double ambient_read(void) { return 1000.0; }

int main(void)
{
    const uint8_t serial[14] = {
        'A', 'B', 'C', 'D', 'E', 'F', '1', '2', '3', '4', '5', '6', '7', '8'
    };
    const uint8_t time_record[21] = {
        1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U, 9U, 10U, 11U,
        12U, 13U, 14U, 15U, 16U, 17U, 18U, 19U, 20U, 21U
    };
    uint8_t calibration_data[36] = {0U};
    struct open_cfw_pt_board_backend board;
    struct open_cfw_pt_platform_backend backend;
    struct open_cfw_pt_board_backend missing_board;
    struct open_cfw_pt_platform_backend missing_backend;
    const struct open_cfw_pt_board_calls missing_calls = {0};
    uint8_t value = 0U;
    int16_t difference = 0;
    uint32_t frequency = 0U;
    uint8_t duty = 0U;
    uint8_t fixed[36] = {0U};
    int16_t touch[5] = {0};
    char text[32];
    struct open_cfw_pt_session_status session;
    size_t received = 0U;
    unsigned int index;
    uint8_t audio_chunk[210];
    uint16_t audio_bytes = 0U;
    int audio_done = 0;
    const struct open_cfw_pt_board_calls calls = {
        .set_local_lid = set_lid,
        .set_local_level = set_level,
        .set_local_charging = set_charging,
        .codec_mic_delay_1bit = codec_delay,
        .system_data_write = system_write,
        .system_data_get = system_get,
        .system_data_read = system_read,
        .post_input_message_id3 = post_input,
        .product_mode_read = mode_read,
        .product_mode_update = mode_update,
        .touch_proximity = proximity,
        .touch_read_differences = differences,
        .psn_write_otp = write_otp,
        .memory_compare = compare,
        .sensor_calibration_update = calibration,
        .buzzer_start = buzzer_start,
        .buzzer_stop = buzzer_stop,
        .buzzer_frequency_get = buzzer_frequency_get,
        .buzzer_duty_get = buzzer_duty_get,
        .buzzer_update = buzzer_update,
        .onboarding_update = onboarding_update,
        .production_reset = production_reset,
        .charger_test_disable = charger_disable,
        .charger_test_enable = charger_enable,
        .identifier_record_link = &identifier_link,
        .sync_ready = &sync_ready,
        .boolean_flag = &boolean_flag,
        .pair_state = pair_state,
        .pair_state_mutable = pair_state,
        .session_record = session_record,
        .session_record_mutable = session_record,
        .diagnostic_blob_36 = diagnostic_blob,
        .font_version = font_version,
        .display_value = &display_value,
        .display_runtime_flag = &display_runtime_flag,
        .aging_mode = &aging_mode,
        .aging_mode_mutable = &aging_mode,
        .imu_latest_sample = latest_imu,
        .sensor_calibration_initialize = calibration_initialize,
        .sensor_calibration_read = calibration_read,
        .imu_orientation = orientation_read,
        .calibration_reference_matrix = reference_matrix,
        .touch_platform_identifier = &touch_platform_id,
        .apollo_platform_identifier = &apollo_platform_id,
        .codec_platform_identifier = codec_platform_id,
        .file_open = file_open,
        .file_close = file_close,
        .file_read = file_read,
        .file_write = file_write,
        .file_seek = file_seek,
        .file_tell = file_tell,
        .file_size = file_size,
        .file_remove = file_remove,
        .tick_count = tick_count,
        .payload_path = payload_path,
        .file_read_mode = file_read_mode,
        .file_write_mode = file_write_mode,
        .storage_test_path = storage_test_path,
        .storage_required_paths = {
            storage_required_paths[0], storage_required_paths[1],
            storage_required_paths[2], storage_required_paths[3]
        },
        .cleanup_paths = {
            cleanup_paths[0], cleanup_paths[1], cleanup_paths[2]
        },
        .metadata_word = &metadata_word,
        .payload_handle_slot = &payload_handle_slot,
        .payload_active = &payload_active,
        .payload_open_seconds = &payload_open_seconds,
        .ota_set_interface = ota_set_interface,
        .ota_frame_dispatch = ota_frame_dispatch,
        .thread_get_id = thread_get_id,
        .thread_set_priority = thread_set_priority,
        .ota_stock_sequence = &ota_stock_sequence,
        .ota_stock_initialized = &ota_stock_initialized,
        .ota_stock_staging_length = &ota_stock_staging_length,
        .ota_async_data = ota_async_data,
        .ota_async_length = &ota_async_length,
        .ota_async_ready = &ota_async_ready,
        .ota_status = &ota_status,
        .system_reset = system_reset,
        .box_state_updated = box_state_updated,
        .display_postprocess = display_postprocess,
        .font_crc_check_0 = font_crc_check_0,
        .font_crc_check_1 = font_crc_check_1,
        .display_value_mutable = &display_value,
        .hardware_identifier_0 = hardware_id_0,
        .hardware_identifier_1 = hardware_id_1,
        .hardware_identifier_2 = hardware_id_2,
        .imu_who_am_i = imu_who_am_i,
        .mag_who_am_i = mag_who_am_i,
        .display_hardware_identifier = display_hardware_id,
        .ambient_identifier_initialize = ambient_id_initialize,
        .ambient_identifier_assign = ambient_id_assign,
        .ambient_identifier_step_1 = ambient_id_step_1,
        .ambient_identifier_step_2 = ambient_id_step_2,
        .ambient_identifier_low = ambient_id_low,
        .ambient_identifier_high = ambient_id_high,
        .uart_sync_write = uart_sync_write,
        .delay_ticks = delay_ticks,
        .uart_sync_state = uart_sync_state,
        .uart_sync_expected = uart_sync_expected,
        .lens_side = lens_side,
        .lens_sync_send = lens_sync_send,
        .lens_sync_ready = &lens_sync_ready,
        .lens_sync_template_12 = lens_sync_template,
        .screen_show = screen_show,
        .screen_hide = screen_hide,
        .display_state = display_state,
        .display_brightness = display_brightness,
        .display_stage_1 = display_stage_1,
        .display_stage_2 = display_stage_2,
        .display_stage_3 = display_stage_3,
        .display_offset = display_offset,
        .audio_status_get = audio_status_get,
        .firmware_version = firmware_version,
        .audio_path_format = audio_path_format,
        .audio_channel_0_start = audio_channel_0_start,
        .audio_channel_0_stop = audio_channel_0_stop,
        .audio_channel_1_start = audio_channel_1_start,
        .audio_channel_1_stop = audio_channel_1_stop,
        .audio_codec_route = audio_codec_route,
        .audio_channel_0_template_12 = audio_template_0,
        .audio_channel_1_template_12 = audio_template_1,
        .audio_handle_slot = &audio_handle_slot,
        .audio_active = &audio_active,
        .audio_length_state = &audio_length_state,
        .audio_offset_state = &audio_offset_state,
        .audio_path_state_32 = audio_path_state,
        .system_data_reset_aging = system_data_reset_aging,
        .time_configure = time_configure,
        .time_capture = time_capture,
        .time_configuration = time_configuration,
        .ambient_read = ambient_read,
        .ambient_baseline = &ambient_baseline,
        .ambient_secondary = &ambient_secondary,
    };
#define RUN(op, a0, a1, a2) backend.perform((op), (uintptr_t)(a0), \
    (uintptr_t)(a1), (uintptr_t)(a2), 0U, 0U, backend.context)
#define RUN4(op, a0, a1, a2, a3) backend.perform((op), (uintptr_t)(a0), \
    (uintptr_t)(a1), (uintptr_t)(a2), (uintptr_t)(a3), 0U, \
    backend.context)
#define RUN5(op, a0, a1, a2, a3, a4) backend.perform((op), (uintptr_t)(a0), \
    (uintptr_t)(a1), (uintptr_t)(a2), (uintptr_t)(a3), (uintptr_t)(a4), \
    backend.context)
    if (open_cfw_pt_board_backend_initialize(NULL, &calls, &backend) !=
            OPEN_CFW_PT_INVALID_ARGUMENT ||
        open_cfw_pt_board_backend_initialize(&board, NULL, &backend) !=
            OPEN_CFW_PT_INVALID_ARGUMENT ||
        open_cfw_pt_board_backend_initialize(&board, &calls, NULL) !=
            OPEN_CFW_PT_INVALID_ARGUMENT) return 71;
    if (open_cfw_pt_board_backend_initialize(&board, &calls, &backend) != 0)
        return 1;
    if (backend.perform(OPEN_CFW_PT_OP_COUNT, 0U, 0U, 0U, 0U, 0U,
            backend.context) != OPEN_CFW_PT_HANDLER_FAILED ||
        backend.perform(OPEN_CFW_PT_OP_SET_BOX_DETECTED, 0U, 0U, 0U, 0U,
            0U, NULL) != OPEN_CFW_PT_INVALID_ARGUMENT) return 72;
    if (open_cfw_pt_board_backend_initialize(
            &missing_board, &missing_calls, &missing_backend) != 0 ||
        missing_backend.perform(OPEN_CFW_PT_OP_SET_BOX_DETECTED,
            1U, 0U, 0U, 0U, 0U,
            missing_backend.context) != OPEN_CFW_PT_HANDLER_FAILED) return 73;
    if (RUN(OPEN_CFW_PT_OP_SET_BOX_DETECTED, 1U, 0U, 0U) != 0 ||
        local_lid != 1U) return 2;
    if (RUN(OPEN_CFW_PT_OP_CODEC_DELAY, 0U, 0U, 0U) != 0) return 3;
    if (RUN(OPEN_CFW_PT_OP_STORE_TERMINAL_MODE, 7U, 0U, 0U) != 0 ||
        system_data[5] != 7U) return 4;
    if (RUN(OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE, &value, 0U, 0U) != 0 ||
        value != 7U) return 5;
    if (RUN(OPEN_CFW_PT_OP_POST_INPUT_MESSAGE, 0U, 0U, 0U) != 0 ||
        input_posts != 1U) return 6;
    if (RUN(OPEN_CFW_PT_OP_SET_PRODUCT_MODE, 1U, 0U, 0U) != 0 ||
        RUN(OPEN_CFW_PT_OP_GET_PRODUCT_MODE, &value, 0U, 0U) != 0 ||
        value != 1U) return 7;
    if (RUN(OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC,
            &value, &difference, 0U) != 0 || value != 0x5AU ||
        difference != (int16_t)0xF234) return 8;
    if (RUN(OPEN_CFW_PT_OP_WRITE_PSN_14, serial, sizeof(serial), 0U) != 0 ||
        memcmp(product_serial, serial, sizeof(serial)) != 0) return 9;
    if (RUN(OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36,
            calibration_data, sizeof(calibration_data), 0U) != 0 ||
        calibration_updates != 1U) return 10;
    if (RUN(OPEN_CFW_PT_OP_BUZZER_TEST, 1U, 4000U, 30U) != 0 ||
        buzzer_frequency != 4000U || buzzer_duty != 30U) return 11;
    if (RUN(OPEN_CFW_PT_OP_BUZZER_READ, &frequency, &duty, 0U) != 0 ||
        frequency != 4000U || duty != 30U) return 12;
    if (RUN(OPEN_CFW_PT_OP_BUZZER_WRITE, 9000U, 55U, 0U) != 0 ||
        buzzer_frequency != 9000U || buzzer_duty != 55U) return 13;
    if (RUN(OPEN_CFW_PT_OP_UPDATE_ONBOARDING, 1U, 0U, 0U) != 0 ||
        onboarding != 1U) return 14;
    if (RUN(OPEN_CFW_PT_OP_PRODUCTION_RESET, 0U, 0U, 0U) != 0 ||
        reset_actions != 1U) return 15;
    if (RUN(OPEN_CFW_PT_OP_SET_CHARGER_TEST, 1U, 0U, 0U) != 0 ||
        charger_test != 1U ||
        RUN(OPEN_CFW_PT_OP_SET_CHARGER_TEST, 0U, 0U, 0U) != 0 ||
        charger_test != 0U) return 16;
    if (RUN(OPEN_CFW_PT_OP_READ_IDENTIFIER_6,
            fixed, 6U, 0U) != 0 || fixed[0] != 1U || fixed[5] != 6U)
        return 17;
    if (RUN(OPEN_CFW_PT_OP_READ_SYSTEM_TEXT, 1U, text, sizeof(text)) != 0 ||
        strcmp(text, board_serial) != 0) return 18;
    if (RUN(OPEN_CFW_PT_OP_WRITE_TIME_21,
            time_record, sizeof(time_record), 0U) != 0 ||
        memcmp(board_serial, time_record, sizeof(time_record)) != 0) return 44;
    if (RUN(OPEN_CFW_PT_OP_SET_SYNC_READY, 1U, 0U, 0U) != 0 ||
        sync_ready != 1U) return 19;
    if (RUN(OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG, &value, 0U, 0U) != 0 ||
        value != 1U) return 20;
    pair_state[0x2CU] = 9U;
    pair_state[0x2DU] = 10U;
    if (RUN(OPEN_CFW_PT_OP_READ_PAIR_STATE, &value, &duty, 0U) != 0 ||
        value != 9U || duty != 10U) return 21;
    session_record[0x48U] = 1U;
    session_record[0x4CU] = 2U;
    session_record[0x50U] = 3U;
    session_record[0x70U] = 4U;
    session_record[0x74U] = 5U;
    session_record[0x78U] = 6U;
    session_record[0x98U] = 7U;
    session_record[0x9CU] = 8U;
    session_record[0xA0U] = 9U;
    session_record[0xA8U] = 10U;
    session_record[0xA9U] = 11U;
    session_record[0xAAU] = 12U;
    session_record[0xABU] = 13U;
    if (RUN(OPEN_CFW_PT_OP_READ_SESSION_STATUS,
            &session, 0U, 0U) != 0 || session.state != 12U ||
        session.reference.hour != 1U || session.reference.minute != 2U ||
        session.reference.second != 3U || session.first.hour != 4U ||
        session.first.minute != 5U || session.first.second != 6U ||
        session.second.hour != 7U || session.second.minute != 8U ||
        session.second.second != 9U || session.flag_a != 11U ||
        session.flag_b != 10U || session.flag_c != 13U) return 40;
    if (RUN4(OPEN_CFW_PT_OP_SET_BOX_STATE, 70U, 1U, 1U, 1U) != 0 ||
        local_level != 70U || local_charging != 1U || local_lid != 1U)
        return 41;
    memset(pair_state, 0, sizeof(pair_state));
    pair_state[4U] = 0x44U;
    pair_state[8U] = 250U;
    pair_state[0x0CU] = 0xF9U;
    pair_state[0x0DU] = 0xFFU;
    pair_state[0x0EU] = 0xFFU;
    pair_state[0x0FU] = 0xFFU;
    pair_state[0x10U] = 0x2CU;
    pair_state[0x11U] = 1U;
    pair_state[0x14U] = 1U;
    if (RUN(OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7,
            fixed, 7U, 0U) != 0 || fixed[0] != 0x44U ||
        fixed[1] != 0x51U || fixed[2] != 1U || fixed[3] != 7U ||
        fixed[4] != 1U || fixed[5] != 1U || fixed[6] != 0x2CU)
        return 42;
    if (RUN(OPEN_CFW_PT_OP_READ_BOX_DETAIL_6,
            fixed, 6U, 0U) != 0 || fixed[0] != 1U ||
        fixed[1] != 0U || fixed[2] != 250U || fixed[3] != 0x44U ||
        fixed[4] != 1U || fixed[5] != 1U) return 43;
    value = 0xFFU;
    if (RUN(OPEN_CFW_PT_OP_STORAGE_SELF_TEST,
            &value, 0U, 0U) != 0 || value != 0U) return 56;
    for (index = 0U; index < sizeof(fake_file_data); ++index)
        fake_file_data[index] = (uint8_t)index;
    if (RUN(OPEN_CFW_PT_OP_STORAGE_READY, &value, 0U, 0U) != 0 ||
        value != 1U) return 45;
    if (RUN(OPEN_CFW_PT_OP_READ_METADATA_32,
            fixed, 32U, 0U) != 0 || fixed[0] != 0U || fixed[31] != 31U ||
        metadata_word != 0x1F1E1D1CU) return 46;
    if (RUN(OPEN_CFW_PT_OP_OPEN_PAYLOAD, 0U, 0U, 0U) != 0 ||
        payload_handle_slot != fake_file_data || payload_active != 1U ||
        payload_open_seconds != 123U) return 47;
    if (RUN4(OPEN_CFW_PT_OP_READ_PAYLOAD_AT,
            32U, fixed, 4U, &received) != 0 || received != 4U ||
        fixed[0] != 32U || fixed[3] != 35U) return 48;
    if (RUN(OPEN_CFW_PT_OP_CLOSE_PAYLOAD, 0U, 0U, 0U) != 0 ||
        payload_handle_slot != NULL || payload_active != 0U ||
        payload_open_seconds != 0U) return 49;
    if (RUN(OPEN_CFW_PT_OP_OTA_INITIALIZE, 0U, 0U, 0U) != 0 ||
        ota_interface != 1U || ota_stock_sequence != 0U ||
        ota_stock_initialized != 1U || ota_stock_staging_length != 0U)
        return 50;
    if (RUN(OPEN_CFW_PT_OP_OTA_DISPATCH, 0U, 0U, 0U) != 0 ||
        ota_frame_command != 0xC0U || ota_frame_length != 1U ||
        ota_frame[0] != 0U || ota_priority != 0x2F) return 51;
    if (RUN(OPEN_CFW_PT_OP_OTA_DISPATCH,
            1U, fake_file_data, 128U) != 0 || ota_frame_length != 129U ||
        ota_frame[0] != 1U || ota_frame[1] != 0U || ota_frame[128] != 127U)
        return 52;
    if (RUN(OPEN_CFW_PT_OP_OTA_DISPATCH, 2U, 0U, 0U) != 0 ||
        ota_frame_length != 1U || ota_frame[0] != 2U) return 53;
    if (RUN(OPEN_CFW_PT_OP_OTA_DISPATCH,
            4U, fake_file_data, 16U) != 0 || ota_async_length != 16U ||
        ota_async_ready != 1U || memcmp(
            ota_async_data, fake_file_data, 16U) != 0) return 54;
    value = 0U;
    if (RUN(OPEN_CFW_PT_OP_OTA_STATUS, &value, 0U, 0U) != 0 ||
        value != 7U) return 55;
    value = 0xFFU;
    if (RUN(OPEN_CFW_PT_OP_UART_SYNC_TEST, &value, 0U, 0U) != 0 ||
        value != 0U) return 58;
    value = 0xFFU;
    if (RUN(OPEN_CFW_PT_OP_LENS_SYNC_TEST, &value, 0U, 0U) != 0 ||
        value != 0U || lens_sync_payload[4] != 1U ||
        lens_sync_payload[5] != 2U) return 59;
    diagnostic_blob[0] = 0xAAU;
    diagnostic_blob[35] = 0x55U;
    if (RUN(OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36,
            fixed, sizeof(fixed), 0U) != 0 || fixed[0] != 0xAAU ||
        fixed[35] != 0x55U) return 22;
    if (RUN(OPEN_CFW_PT_OP_READ_FONT_VERSION, 0U, text, sizeof(text)) != 0 ||
        strcmp(text, "1.2.3") != 0) return 23;
    if (RUN(OPEN_CFW_PT_OP_READ_DISPLAY_VALUE, &value, 0U, 0U) != 0 ||
        value != 0x71U) return 24;
    if (RUN(OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG, 1U, 0U, 0U) != 0 ||
        display_runtime_flag != 1U ||
        RUN(OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG, 0U, 0U, 0U) != 0 ||
        display_runtime_flag != 0U) return 25;
    value = 0U;
    if (RUN(OPEN_CFW_PT_OP_GET_AGING_MODE, &value, 0U, 0U) != 0 ||
        value != 1U) return 26;
    if (RUN(OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36,
            fixed, sizeof(fixed), 0U) != 0 ||
        memcmp(fixed, imu_sample, sizeof(fixed)) != 0) return 27;
    if (RUN(OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES, touch, 0U, 0U) != 0 ||
        touch[4] != (int16_t)0xF234) return 28;
    {
        int matches = 0;
        uint8_t orientation_bytes[12];
        if (RUN(OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION,
                &matches, orientation_bytes, 0U) != 0 || matches != 1 ||
            memcmp(orientation_bytes, orientation,
                sizeof(orientation_bytes)) != 0) return 29;
    }
    if (RUN(OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER,
            0U, &frequency, 0U) != 0 || frequency != touch_platform_id ||
        RUN(OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER,
            1U, &frequency, 0U) != 0 || frequency != apollo_platform_id ||
        RUN(OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER,
            2U, &frequency, 0U) != 0 || frequency != 0x55667788U)
        return 30;
    if (RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            0U, &frequency, 0U) != 0 || frequency != 0xAABBCCDDU ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            1U, &frequency, 0U) != 0 || frequency != 0x00223344U ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            2U, &frequency, 0U) != 0 || frequency != 0x23U ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            3U, &frequency, 0U) != 0 || frequency != 0x01020304U ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            4U, &frequency, 0U) != 0 || frequency != 0x05060708U ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            5U, &frequency, 0U) != 0 || frequency != 0xABCDU ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            6U, &frequency, 0U) != 0 || frequency != 0xABCD1234U ||
        RUN(OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER,
            7U, &frequency, 0U) != 0 || frequency != touch_platform_id)
        return 57;
    display_stage_mask = 0U;
    if (RUN(OPEN_CFW_PT_OP_SET_TEST_SCREEN, 0x10FU, 1U, 0U) != 0 ||
        display_active != 1U || last_screen_id != 0x10FU ||
        last_brightness_delay != 50U || last_brightness_value != 10U ||
        display_stage_mask != 7U) return 31;
    if (RUN(OPEN_CFW_PT_OP_SET_TEST_SCREEN, 0x10FU, 0U, 0U) != 0 ||
        display_active != 0U) return 60;
    display_stage_mask = 0U;
    if (RUN(OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS, 12U, 34U, 1U) != 0 ||
        pair_state[0x2CU] != 12U || pair_state[0x2DU] != 34U ||
        system_data[3] != 12U || system_data[4] != 34U ||
        display_active != 1U || last_screen_id != 0x10BU ||
        display_offset_first != 12U || display_offset_second != 34U ||
        display_stage_mask != 7U) return 61;
    if (RUN(OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5,
            fixed, 5U, 0U) != 0 || fixed[0] != 2U || fixed[1] != 2U ||
        fixed[2] != 6U || fixed[3] != 10U || fixed[4] != 0xA5U)
        return 62;
    if (RUN5(OPEN_CFW_PT_OP_AUDIO_READ_CHUNK,
            0U, 0U, audio_chunk, &audio_bytes, &audio_done) != 0 ||
        audio_bytes != 210U || audio_done != 0 || audio_chunk[0] != 0U ||
        audio_chunk[209] != 209U) return 63;
    if (RUN5(OPEN_CFW_PT_OP_AUDIO_READ_CHUNK,
            0U, 0U, audio_chunk, &audio_bytes, &audio_done) != 0 ||
        audio_bytes != 90U || audio_done != 1 || audio_chunk[0] != 210U ||
        audio_chunk[89] != 43U) return 64;
    if (RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 0U, 0U, 9U) != 0 ||
        audio_action != 1U || audio_argument != 9U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 0U, 1U, 0U) != 0 ||
        audio_action != 2U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 1U, 0U, 0U) != 0 ||
        audio_action != 3U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 1U, 1U, 0U) != 0 ||
        audio_action != 4U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 0U, 2U, 0U) != 0 ||
        audio_route_channel != 1U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 1U, 2U, 0U) != 0 ||
        audio_route_channel != 0U ||
        RUN(OPEN_CFW_PT_OP_AUDIO_CONTROL, 0U, 3U, 0U) != 0 ||
        lens_sync_payload[0] != 0x10U || lens_sync_payload[4] != 1U ||
        lens_sync_payload[5] != 2U) return 65;
    if (RUN(OPEN_CFW_PT_OP_SET_AGING_MODE, 0U, 0U, 0U) != 0 ||
        aging_mode != 0U || session_record[0xABU] != 1U ||
        session_record[0x58U] != 1U || session_record[0x7FU] != 40U)
        return 66;
    if (RUN(OPEN_CFW_PT_OP_SET_AGING_MODE, 1U, 0U, 0U) != 0 ||
        aging_mode != 1U || aging_resets != 1U ||
        configured_time_value != 0x12345678U || configured_timezone != -5 ||
        last_screen_id != 0x104U || session_record[0x30U] != 1U ||
        session_record[0x57U] != 40U) return 67;
    value = 0xFFU;
    frequency = 0U;
    if (RUN(OPEN_CFW_PT_OP_CALIBRATE_AMBIENT,
            4U, &frequency, &value) != 0 || frequency != 1000U ||
        value != 0U || ambient_baseline != 1000U) return 68;
    value = 0xFFU;
    frequency = 0U;
    if (RUN(OPEN_CFW_PT_OP_CALIBRATE_AMBIENT,
            1U, &frequency, &value) != 0 || frequency != 1000U ||
        value != 0U || ambient_secondary != 1000U ||
        memcmp(session_record + 0x28U, "\0\0\0\0", 4U) == 0) return 69;
    memset(fixed, 0xFF, sizeof(fixed));
    if (RUN(OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32,
            fixed, 32U, 0U) != 0 ||
        fixed[0] != 0xE8U || fixed[1] != 0x03U ||
        fixed[2] != 0U || fixed[3] != 0U ||
        (fixed[28] | fixed[29] | fixed[30] | fixed[31]) == 0U)
        return 70;
    {
        uint8_t request[5] = {0U, 0U, 0U, 0U, 0U};
        uint8_t response[9] = {0U};
        response[4] = 0x01U;
        response[8] = 0U;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            system_resets != 1U) return 74;
        response[4] = 0x06U;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            cleanup_removals != 7U) return 75;
        response[4] = 0x0BU;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            system_resets != 2U) return 76;
        response[4] = 0x13U;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            box_state_updates != 1U) return 77;
        aging_mode = 1U;
        response[4] = 0x3EU;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            aging_mode != 0U || system_resets != 3U) return 78;
        ota_async_ready = 1U;
        ota_async_length = 4U;
        ota_async_data[0] = 0xA5U;
        response[4] = 0x54U;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            ota_async_ready != 0U || ota_async_length != 0U ||
            ota_frame_command != 0xC1U || ota_frame_length != 4U ||
            ota_frame[0] != 0xA5U) return 79;
        response[4] = 0x66U;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            display_postprocesses != 1U) return 80;
        response[4] = 0x6CU;
        display_value = 0xFFU;
        if (RUN4(OPEN_CFW_PT_OP_POST_RESPONSE,
                request, sizeof(request), response, sizeof(response)) != 0 ||
            display_value != 3U) return 81;
    }
    return 0;
#undef RUN
#undef RUN4
#undef RUN5
}
