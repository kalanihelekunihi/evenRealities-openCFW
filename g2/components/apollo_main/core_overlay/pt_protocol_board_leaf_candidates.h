/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_BOARD_LEAF_CANDIDATES_H
#define OPEN_CFW_PT_PROTOCOL_BOARD_LEAF_CANDIDATES_H

#include <stdint.h>

typedef struct open_cfw_pt_time_record {
    uint32_t read_error;
    uint32_t weekday;
    uint32_t century_bit;
    uint32_t year;
    uint32_t month;
    uint32_t day;
    uint32_t hour;
    uint32_t minute;
    uint32_t second;
    uint32_t hundredths;
} open_cfw_pt_time_record;

uint8_t open_cfw_pt_display_postprocess_state_0(void);
uint8_t open_cfw_pt_display_postprocess_state_1(void);
uint8_t open_cfw_pt_display_postprocess_state_2(void);
void open_cfw_pt_seconds_to_time(uint32_t seconds, void *output);
int32_t open_cfw_pt_time_to_seconds(const void *input);
void open_cfw_pt_time_output(int32_t seconds, void *output);
void open_cfw_pt_system_reset_inner(void);
void open_cfw_pt_display_buffer_write(void *destination, uintptr_t source,
                                      uint32_t length);
void *open_cfw_pt_lens_sync_allocate(uint32_t size);
void open_cfw_pt_input_message_send(const void *message);
void open_cfw_pt_codec_mic_enable(uint32_t enabled);
void open_cfw_pt_pdm_mic_enable(uint32_t enabled);
void open_cfw_pt_audio_path_format_provider(uint8_t selector,
                                            uint16_t identifier,
                                            char *path, uint32_t capacity);
void open_cfw_pt_audio_register(uint32_t listener, uint32_t mode,
                                const void *callback);
int open_cfw_pt_audio_remove(uint32_t listener, uint32_t mode);
void open_cfw_pt_audio_unregister(uint32_t mode);
void open_cfw_pt_ambient_assign(void *field, uint32_t value);
uint16_t open_cfw_pt_ambient_sample(void *field);
uint32_t open_cfw_pt_ambient_raw_read(uint32_t register_address);
void open_cfw_pt_font_xip_acquire(void);
void open_cfw_pt_font_xip_release(void);
void open_cfw_pt_display_postprocess_commit(void);

const uint8_t *open_cfw_pt_board_display_state(void);
uint32_t open_cfw_pt_board_codec_platform_identifier(void);
void open_cfw_pt_board_buzzer_start(uint32_t frequency_hz,
                                    uint8_t duty_percent);
void open_cfw_pt_board_buzzer_stop(void);
int open_cfw_pt_board_hardware_identifier_0(uint32_t *value);
int open_cfw_pt_board_hardware_identifier_1(uint32_t *value);
int open_cfw_pt_board_hardware_identifier_2(uint32_t *value);
void open_cfw_pt_board_charger_test_disable(void);
void open_cfw_pt_board_charger_test_enable(void);
int open_cfw_pt_board_uart_sync_write(const uint8_t *data, uint32_t length,
                                      uint32_t timeout);
const uint8_t *open_cfw_pt_board_audio_status_get(uint32_t index);
void open_cfw_pt_board_audio_codec_route(uint32_t code, uint32_t enabled);
void open_cfw_pt_board_audio_channel_0_start(uint8_t selector);
void open_cfw_pt_board_audio_channel_0_stop(void);
void open_cfw_pt_board_audio_channel_1_start(void);
void open_cfw_pt_board_audio_channel_1_stop(void);
void open_cfw_pt_board_display_stage_1(uint32_t value);
void open_cfw_pt_board_display_stage_2(uint32_t first, uint32_t second);
void open_cfw_pt_board_display_stage_3(uint32_t value);
uint32_t open_cfw_pt_board_display_hardware_identifier(void);
void open_cfw_pt_board_display_brightness(uint32_t delay, uint32_t period,
                                          uint32_t brightness);
void open_cfw_pt_board_display_offset(uint8_t first, uint8_t second);
void open_cfw_pt_board_screen_show(uint16_t screen_id, uint32_t argument1,
                                   uint32_t argument2);
void open_cfw_pt_board_screen_hide(uint16_t screen_id, uint32_t argument1,
                                   uint32_t argument2);
int open_cfw_pt_board_lens_sync_send(uint32_t service, const void *payload,
                                     uint32_t length, uint32_t user_data);
void open_cfw_pt_board_audio_path_format(uint8_t selector, char *path,
                                         uint32_t capacity);
void open_cfw_pt_board_time_capture(void *time_record_40);
void open_cfw_pt_board_time_configure(uint32_t seconds, int timezone);
void open_cfw_pt_board_post_input_message_id3(void);
void open_cfw_pt_board_ambient_identifier_initialize(void);
void open_cfw_pt_board_ambient_identifier_step_1(void *device);
void open_cfw_pt_board_ambient_identifier_step_2(void *device);
uint16_t open_cfw_pt_board_ambient_identifier_low(void *device);
uint16_t open_cfw_pt_board_ambient_identifier_high(void *device);
double open_cfw_pt_board_ambient_read(void);
void open_cfw_pt_board_production_reset(void);
void open_cfw_pt_board_system_reset(void);
void open_cfw_pt_board_display_postprocess(void);
uint8_t open_cfw_pt_font_crc_validate(uint32_t base);
uint8_t open_cfw_pt_board_font_crc_check_0(void);
uint8_t open_cfw_pt_board_font_crc_check_1(void);

#endif
