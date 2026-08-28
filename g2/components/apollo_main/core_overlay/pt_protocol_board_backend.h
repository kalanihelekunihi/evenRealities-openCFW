/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_BOARD_BACKEND_H
#define OPEN_CFW_PT_PROTOCOL_BOARD_BACKEND_H

#include <stddef.h>
#include <stdint.h>

#include "pt_protocol_platform_adapter.h"

/*
 * Typed seams for all 56 reconstructed G2 product-test board operations.
 * A host can supply fakes; the production initializer binds the authenticated
 * Apollo layout through 83 callable entries and 53 stock-layout data entries.
 * Forty-three callables redirect to existing source overlays and the 40
 * formerly retained callables are source-routed to admitted semantic-C
 * providers. Those providers are not a closed source graph: their second-order
 * ABI retains 39 fixed-address callable bindings (37 unique entries), plus 33
 * separately classified fixed data/address bindings. The 53 stock-layout data
 * entries in this table are a deliberately supported ABI: 17 authenticated
 * immutable-flash values and 36 runtime-SRAM state/buffer bindings. The
 * production table is installed by the lazy bootstrap reached from the fixed
 * legacy entry veneer.
 */
struct open_cfw_pt_board_calls {
    void (*set_local_lid)(uint8_t value);
    void (*set_local_level)(uint8_t value);
    void (*set_local_charging)(uint8_t value);
    int32_t (*codec_mic_delay_1bit)(void);
    int (*system_data_write)(uint8_t index, const void *data);
    void *(*system_data_get)(uint8_t index);
    void *(*system_data_read)(uint8_t index);
    void (*post_input_message_id3)(void);
    uint8_t (*product_mode_read)(void);
    void (*product_mode_update)(uint8_t mode);
    uint8_t (*touch_proximity)(void);
    int32_t (*touch_read_differences)(uint8_t data[10]);
    int (*psn_write_otp)(const char *serial);
    int (*memory_compare)(const void *left, const void *right,
                          unsigned int length);
    void (*sensor_calibration_update)(const float *vector_a,
                                      const float *vector_b,
                                      const float matrix[9]);
    void (*buzzer_start)(uint32_t frequency_hz, uint8_t duty_percent);
    void (*buzzer_stop)(void);
    uint32_t (*buzzer_frequency_get)(void);
    uint8_t (*buzzer_duty_get)(void);
    void (*buzzer_update)(uint32_t frequency_hz, uint8_t duty_percent);
    int (*onboarding_update)(uint8_t index, const uint8_t *value);
    void (*production_reset)(void);
    void (*charger_test_disable)(void);
    void (*charger_test_enable)(void);
    const uint8_t *const *identifier_record_link;
    volatile uint8_t *sync_ready;
    const uint8_t *boolean_flag;
    const uint8_t *pair_state;
    volatile uint8_t *pair_state_mutable;
    const uint8_t *session_record;
    uint8_t *session_record_mutable;
    const uint8_t *diagnostic_blob_36;
    const char *(*font_version)(void);
    const uint8_t *display_value;
    volatile uint8_t *display_runtime_flag;
    const uint8_t *aging_mode;
    volatile uint8_t *aging_mode_mutable;
    const float *(*imu_latest_sample)(void);
    void (*sensor_calibration_initialize)(void);
    int (*sensor_calibration_read)(float vector_a[3], float vector_b[3],
                                   float matrix[9]);
    const float *(*imu_orientation)(void);
    const float *calibration_reference_matrix;
    const uint32_t *touch_platform_identifier;
    const uint32_t *apollo_platform_identifier;
    uint32_t (*codec_platform_identifier)(void);
    void *(*file_open)(const void *path, const char *mode);
    int (*file_close)(void *file);
    unsigned int (*file_read)(void *destination, unsigned int element_size,
                              unsigned int element_count, void *file);
    unsigned int (*file_write)(const void *source, unsigned int element_size,
                               unsigned int element_count, void *file);
    int (*file_seek)(void *file, int offset, unsigned int origin);
    int (*file_tell)(void *file);
    int (*file_size)(void *file);
    int (*file_remove)(const void *path);
    uint32_t (*tick_count)(void);
    const char *payload_path;
    const char *file_read_mode;
    const char *file_write_mode;
    const char *storage_test_path;
    const char *storage_required_paths[4];
    const char *cleanup_paths[3];
    volatile uint32_t *metadata_word;
    void *volatile *payload_handle_slot;
    volatile uint8_t *payload_active;
    volatile uint32_t *payload_open_seconds;
    void (*ota_set_interface)(uint32_t interface, uint32_t service,
                              void *callback, uint32_t enabled);
    int (*ota_frame_dispatch)(uint8_t command, const uint8_t *payload,
                              uint16_t length);
    void *(*thread_get_id)(void);
    int (*thread_set_priority)(void *thread, int priority);
    volatile uint8_t *ota_stock_sequence;
    volatile uint8_t *ota_stock_initialized;
    volatile uint32_t *ota_stock_staging_length;
    uint8_t *ota_async_data;
    volatile uint32_t *ota_async_length;
    volatile uint8_t *ota_async_ready;
    const uint8_t *ota_status;
    void (*system_reset)(void);
    void (*box_state_updated)(void);
    void (*display_postprocess)(void);
    uint8_t (*font_crc_check_0)(void);
    uint8_t (*font_crc_check_1)(void);
    volatile uint8_t *display_value_mutable;
    int (*hardware_identifier_0)(uint32_t *value);
    int (*hardware_identifier_1)(uint32_t *value);
    int (*hardware_identifier_2)(uint32_t *value);
    int (*imu_who_am_i)(uint32_t *value);
    int (*mag_who_am_i)(uint32_t *value);
    uint32_t (*display_hardware_identifier)(void);
    void (*ambient_identifier_initialize)(void);
    void (*ambient_identifier_assign)(void *device);
    void (*ambient_identifier_step_1)(void *device);
    void (*ambient_identifier_step_2)(void *device);
    uint16_t (*ambient_identifier_low)(void *device);
    uint16_t (*ambient_identifier_high)(void *device);
    int (*uart_sync_write)(const uint8_t *data, uint32_t length,
                           uint32_t timeout);
    int (*delay_ticks)(uint32_t ticks);
    volatile uint8_t *uart_sync_state;
    const uint8_t *uart_sync_expected;
    uint8_t (*lens_side)(void);
    int (*lens_sync_send)(uint32_t service, const void *payload,
                          uint32_t length, uint32_t reserved);
    volatile uint8_t *lens_sync_ready;
    const uint8_t *lens_sync_template_12;
    void (*screen_show)(uint16_t screen_id, uint32_t argument1,
                        uint32_t argument2);
    void (*screen_hide)(uint16_t screen_id, uint32_t argument1,
                        uint32_t argument2);
    const uint8_t *(*display_state)(void);
    void (*display_brightness)(uint32_t delay, uint32_t period,
                               uint32_t brightness);
    void (*display_stage_1)(uint32_t value);
    void (*display_stage_2)(uint32_t first, uint32_t second);
    void (*display_stage_3)(uint32_t value);
    void (*display_offset)(uint8_t first, uint8_t second);
    const uint8_t *(*audio_status_get)(uint32_t index);
    const char *firmware_version;
    void (*audio_path_format)(uint8_t selector, char *path,
                              uint32_t capacity);
    void (*audio_channel_0_start)(uint8_t argument);
    void (*audio_channel_0_stop)(void);
    void (*audio_channel_1_start)(void);
    void (*audio_channel_1_stop)(void);
    void (*audio_codec_route)(uint32_t code, uint32_t channel_0);
    const uint8_t *audio_channel_0_template_12;
    const uint8_t *audio_channel_1_template_12;
    void *volatile *audio_handle_slot;
    volatile uint8_t *audio_active;
    volatile uint32_t *audio_length_state;
    volatile uint32_t *audio_offset_state;
    uint8_t *audio_path_state_32;
    void (*system_data_reset_aging)(void);
    void (*time_configure)(uint32_t value, int timezone);
    void (*time_capture)(void *time_record_40);
    const uint8_t *time_configuration;
    double (*ambient_read)(void);
    volatile uint32_t *ambient_baseline;
    volatile uint32_t *ambient_secondary;
};

struct open_cfw_pt_board_backend {
    const struct open_cfw_pt_board_calls *calls;
};

/*
 * The caller owns calls. It must remain valid and immutable for the full
 * lifetime of board and the platform backend initialized from board.
 */
int open_cfw_pt_board_backend_initialize(
    struct open_cfw_pt_board_backend *board,
    const struct open_cfw_pt_board_calls *calls,
    struct open_cfw_pt_platform_backend *backend);

int open_cfw_pt_board_backend_initialize_production(
    struct open_cfw_pt_board_backend *board,
    struct open_cfw_pt_platform_backend *backend);

#endif
