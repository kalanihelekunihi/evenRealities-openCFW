/* Product-test command handlers (flash burn check, UART sync, ship mode, PSN,
 * aging test, buzzer, aging result, chip IDs, firmware versions, peer sync,
 * mic delay, production OTA), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x572c64..0x57301a, 0x57303c..0x5735e2, 0x573c58..0x573f60,
 * 0x573f88..0x5741ca, 0x574464..0x575360, 0x57536c..0x575ac0 (the IMU/lux
 * calibration handlers 0x573604, 0x5738d0 and 0x5741e0 use double-precision VFP
 * and are in pt_procsr_calib.c).
 *
 * Every handler is reached through pt_protocol_dispatch (0x56f4a0) as
 * handler(payload, length, rsp, rsp_len): payload[0] is the command byte,
 * payload[3] the data length and arguments start at payload[4]. The response is
 * [rsp_cmd][0x01][type][data_len][data...]; the symbol table's pt_cmd_XX names
 * do not match the command bytes, so each handler comment gives the real
 * command (= rsp_cmd) and the stock __func__ name. Data byte 0 is the status:
 * 0 ok, 1 fail, 3 invalid argument, 5 not in product-test mode. A NULL buffer
 * or short frame returns UINT32_MAX with no response; pt_handler_result itself returns int32_t -1.
 *
 * Production OTA (commands 0x52..0x55): the host streams the image in
 * 1000-byte packets, each carrying a one-byte sequence ("timestamp") and a
 * CRC16 trailer. Packets are gathered in a 7024-byte RAM buffer; once it holds
 * more than 5999 bytes (or on the last packet) it is copied to the frame buffer
 * consumed by pt_production_mode_orchestrate, which feeds semantic_OtaFrameDispatch. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_nvdb.h"
#include "g2_als.h"
#include "g2_kvdb.h"

#define PT_PRODUCT_TEST_MODE 1u
#define PT_OTA_FRAME_COMMAND 0xc0u   /* semantic_OtaFrameDispatch command */
#define PT_OTA_HEADER_SIZE 0x80u     /* EVEN_OTA_FILE_HEADER_SIZE */
#define PT_OTA_PACKET_SIZE 1000
#define PT_OTA_FLUSH_THRESHOLD 5999u
#define PT_OTA_RX_BUFFER_SIZE 0x1b70u
#define PT_AGING_DISPLAY_APP 0x104u
#define PT_PEER_SYNC_APP 0x102u
#define PT_SYNC_POLLS 40u            /* 1-tick polls of the UART reply */

extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 nvSysDt */
#define SYS_DT ((g2_nvdb_sys_dt_t *)(void *)display_driver_ratio_cells_20003994)

extern uint8_t g2_uart_command[];                        /* RAM 0x20074080, [0] = 1 while waiting, reply at +1 */
extern volatile uint8_t g2_dev_shipmode_pending;         /* RAM 0x20075003 */
extern volatile uint8_t g2_pt_peer_sync_ack_20075004;    /* RAM 0x20075004, set by the peer sync reply */
extern uint8_t g2_pt_ota_sequence_20075005;              /* RAM 0x20075005, upgrade_file_timestamp */
extern uint8_t g2_ota_crc_failed;                        /* RAM 0x20075007, g_production_ota_crc_result */
extern volatile uint8_t g2_pt_ota_frame_pending;         /* RAM 0x20075008 */
extern volatile uint8_t g2_dev_status_pin_inhibit;       /* RAM 0x2007500a */
extern volatile uint8_t g2_pdm_production_bypass;        /* RAM 0x20075019, aging/production test active */
extern uint32_t g2_pt_ota_rx_fill_200748dc;              /* RAM 0x200748dc */
extern volatile uint32_t g2_pt_ota_frame_length;         /* RAM 0x200748e0 */
extern uint8_t g2_pt_ota_rx_buffer_20058388[PT_OTA_RX_BUFFER_SIZE]; /* RAM 0x20058388 */
extern uint8_t g2_pt_ota_frame_buffer[];                 /* RAM 0x20059ef8 */
extern uint8_t g2_touch_version_bytes[4];                /* RAM 0x20074508, last raw version reply */
extern uint8_t g2_gx8002_version[4];                     /* RAM 0x20074940, last version read */
extern g2_kvdb_time_t g2_kvdb_time_record;               /* RAM 0x2000380c */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t g2_log_module_length(const char *text);                        /* strlen 0x44a43c */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length);   /* memcmp 0x4751c8 */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t length, const uint16_t *seed);
extern void *file_open(const char *path, const char *mode);                    /* 0x474550 */
extern int32_t file_close(void *file);                                         /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern void *file_heap_allocate(uint32_t size);                                /* 0x474cd2 */
extern void file_heap_free(void *ptr);                                         /* 0x474d16 */
extern int32_t osDelay(uint32_t ticks);                                        /* 0x449376 */
extern void *osThreadGetId(void);                                              /* 0x4491aa */
extern int32_t osThreadSetPriority(void *thread, int32_t priority);            /* 0x4491b2 */
extern uint8_t productModeGet(void);                                           /* 0x4abe60 */
extern uint8_t *display_driver_brightness_ratio_cell_4af73a(uint32_t index);  /* SVC_NvdbGetSysData */
extern uint32_t audio_uart_sync_send(const void *bytes, uint32_t size, uint32_t timeout); /* uart_sync_write 0x541790 */
extern uint32_t audio_uart_request_send(uint32_t app, const void *bytes, uint32_t length, uint32_t id); /* SendDataToPeer 0x4651e0 */
extern int32_t audio_uart_slave_display_start(uint32_t, const void *, uint32_t); /* 0x4441ec */
extern int32_t audio_uart_slave_display_stop(uint32_t, const void *, uint32_t);  /* 0x4443cc */
extern uint32_t display_driver_case4_apply(uint32_t, uint32_t, uint32_t);        /* uled_mspi_setBrightness 0x4ca1ee */
extern uint32_t display_driver_uled_mode_45a568(void);                          /* own role, 1 = left */
extern void SVC_SystemTimeSync(uint32_t epoch, int8_t zone);                   /* 0x44a1fe */
extern void service_time_current_calendar_get(void *out);                      /* 0x44a19a, am_hal_rtc_time_t */
extern int32_t calculate_rtc_time_diff_seconds_56f178(const g2_nvdb_aging_time_t *end,
                                                      const g2_nvdb_aging_time_t *start);
extern void DRV_BuzzerStart(uint32_t frequency, uint8_t duty);                 /* 0x502c88 */
extern void DRV_BuzzerStop(void);                                              /* 0x502d4c */
extern int32_t input_tick_read(uint32_t *out);                                 /* 0x512c84, apb510_get_chip_id */
extern int32_t mx25u25643g_get_device_id_4700b4(uint32_t *id);
extern int32_t npmx_get_device_id_512b20(uint32_t *device_id);
extern int32_t DRV_IMUReadWhoAmI(uint32_t *id);                                /* 0x4a6456 */
extern int32_t DRV_MAGReadWhoAmI(uint32_t *id);                                /* 0x4a64c8 */
extern uint16_t uled_safe_get_chip_id(void);                                   /* 0x4ca070 */
extern void pt_sensor_rail_power_on_58f936(void);
extern void ti_opt3007_assignRegistermap(g2_opt3007_regmap_t *map);           /* 0x5135e0 */
extern void opt3007_mode_continuous_set_58f8cc(g2_opt3007_regmap_t *map);
extern void opt3007_conversion_100ms_set_58f8d8(g2_opt3007_regmap_t *map);
extern uint16_t opt3007_manufacturer_id_get_58f922(g2_opt3007_regmap_t *map);
extern uint16_t opt3007_device_id_get_58f92c(g2_opt3007_regmap_t *map);
extern uint32_t audio_ble_hci_radio_revision_52dee6(void);                     /* BLE image version */
extern int32_t SVC_CodecMicDelay1Bit(void);                                    /* 0x57d870 */
extern void OTA_SetInterface(uint8_t interface);                               /* 0x4487e4 */
extern uint32_t semantic_OtaFrameDispatch(uint8_t command, const uint8_t *data, uint16_t len); /* 0x448670 */

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */
static const char denied[] = "permission denied current mode is not product test mode"; /* ROM 0x721c18 */
static const char denied_c[] = "[pt_protocol_procsr]permission denied current mode is not product test mode"; /* ROM 0x6f586c */

/* get_flash_burn_info */
static const char fn_flash_burn[] = "get_flash_burn_info"; /* ROM 0x782bdc */
static const char flash_join[] = "join in get_flash_burn_info"; /* ROM 0x77059c */
static const char flash_join_c[] = "[pt_protocol_procsr]join in get_flash_burn_info"; /* ROM 0x7373f4 */
static const char fs_write_fail[] = "test write fs fail:%d->%d"; /* ROM 0x7705b8 */
static const char fs_write_fail_c[] = "[pt_protocol_procsr]test write fs fail:%d->%d"; /* ROM 0x737424 */
static const char fs_read_fail[] = "test read fs fail:%d->%d,%s"; /* ROM 0x7705d4 */
static const char fs_read_fail_c[] = "[pt_protocol_procsr]test read fs fail:%d->%d,%s"; /* ROM 0x737454 */
static const char files_check[] = "firmware files exist check: %d,%d,%d,%d => ack=%d"; /* ROM 0x72c64c */
static const char files_check_c[] = "[pt_protocol_procsr]firmware files exist check: %d,%d,%d,%d => ack=%d"; /* ROM 0x6fc4f4 */
static const char flash_ack[] = "get_flash_burn_info ack: %d"; /* ROM 0x77060c */
static const char flash_ack_c[] = "[pt_protocol_procsr]get_flash_burn_info ack: %d"; /* ROM 0x737484 */
static const char path_boot_count[] = "boot_count"; /* ROM 0x78bd20 */
static const char path_ble[] = "/firmware/ble_em9305.bin"; /* ROM 0x7705f0 */
static const char path_box[] = "/firmware/box.bin"; /* ROM 0x782bf0 */
static const char path_codec[] = "/firmware/codec.bin"; /* ROM 0x782c04 */
static const char path_touch[] = "/firmware/touch.bin"; /* ROM 0x782c18 */

/* get_sync_status */
static const char fn_sync[] = "get_sync_status"; /* ROM 0x788510 */
static const char sync_rcv[] = "sync test rcv_buf: %s"; /* ROM 0x77adec */
static const char sync_rcv_c[] = "[pt_protocol_procsr]sync test rcv_buf: %s"; /* ROM 0x742230 */
static const char sync_timeout[] = "sync test timeout"; /* ROM 0x782c2c */
static const char sync_timeout_c[] = "[pt_protocol_procsr]sync test timeout"; /* ROM 0x74d494 */
static const char sync_token[] = "ptSync"; /* ROM 0x78e44c */

/* enter_ship_mode */
static const char fn_ship[] = "enter_ship_mode"; /* ROM 0x788520 */
static const char ship_join[] = "join in enter_ship_mode"; /* ROM 0x77ae04 */
static const char ship_join_c[] = "[pt_protocol_procsr]join in enter_ship_mode"; /* ROM 0x74225c */

/* set_device_sn_info / get_device_sn_info */
static const char fn_sn_set[] = "set_device_sn_info"; /* ROM 0x782c40 */
static const char sn_set_join[] = "join in set_device_sn_info"; /* ROM 0x770628 */
static const char sn_set_join_c[] = "[pt_protocol_procsr]join in set_device_sn_info"; /* ROM 0x7374b4 */
static const char sn_string[] = "The string is: %s\n"; /* ROM 0x782ba0 */
static const char sn_string_c[] = "[pt_protocol_procsr]The string is: %s\n"; /* ROM 0x74d46c */
static const char fn_sn_get[] = "get_device_sn_info"; /* ROM 0x782c54 */
static const char sn_get_join[] = "join in get_device_sn_info"; /* ROM 0x770644 */
static const char sn_get_join_c[] = "[pt_protocol_procsr]join in get_device_sn_info"; /* ROM 0x7374e4 */

/* set_aging_test_info */
static const char fn_aging_set[] = "set_aging_test_info"; /* ROM 0x782c68 */
static const char aging_set_join[] = "join in set_aging_test_info"; /* ROM 0x770660 */
static const char aging_set_join_c[] = "[pt_protocol_procsr]join in set_aging_test_info"; /* ROM 0x737514 */
static const char aging_running[] = "aging test mode is already running"; /* ROM 0x758bc8 */
static const char aging_running_c[] = "[pt_protocol_procsr]aging test mode is already running"; /* ROM 0x721c88 */
static const char aging_enter[] = "enter aging test mode"; /* ROM 0x77ae4c */
static const char aging_enter_c[] = "[pt_protocol_procsr]enter aging test mode"; /* ROM 0x7422e0 */
static const char aging_idle[] = "aging test mode is not running"; /* ROM 0x764410 */
static const char aging_idle_c[] = "[pt_protocol_procsr]aging test mode is not running"; /* ROM 0x72c6e8 */
static const char aging_exit[] = "exit aging test mode"; /* ROM 0x77ae64 */
static const char aging_exit_c[] = "[pt_protocol_procsr]exit aging test mode"; /* ROM 0x74230c */

/* set_buzzer_status */
static const char fn_buzzer[] = "set_buzzer_status"; /* ROM 0x782c7c */
static const char buzzer_join[] = "join in set_buzzer_status"; /* ROM 0x77067c */
static const char buzzer_join_c[] = "[pt_protocol_procsr]join in set_buzzer_status"; /* ROM 0x737544 */
static const char buzzer_open[] = "open buzzer"; /* ROM 0x78bd2c */
static const char buzzer_open_c[] = "[pt_protocol_procsr]open buzzer"; /* ROM 0x764430 */
static const char buzzer_close[] = "close buzzer"; /* ROM 0x788560 */
static const char buzzer_close_c[] = "[pt_protocol_procsr]close buzzer"; /* ROM 0x758bec */
static const char buzzer_error[] = "buzzer status error"; /* ROM 0x782c90 */
static const char buzzer_error_c[] = "[pt_protocol_procsr]buzzer status error"; /* ROM 0x74d4bc */

/* get_aging_mode_info / get_aging_result_info */
static const char fn_aging_mode[] = "get_aging_mode_info"; /* ROM 0x782cb8 */
static const char aging_mode_join[] = "join in get_aging_mode_info"; /* ROM 0x7706b4 */
static const char aging_mode_join_c[] = "[pt_protocol_procsr]join in get_aging_mode_info"; /* ROM 0x7375a4 */
static const char fn_aging_result[] = "get_aging_result_info"; /* ROM 0x77ae7c */
static const char aging_result_join[] = "join in get_aging_result_info"; /* ROM 0x764450 */
static const char aging_result_join_c[] = "[pt_protocol_procsr]join in get_aging_result_info"; /* ROM 0x72c71c */
static const char aging_result[] = "Aging result: total_times=%d, total_time=%d sec, discharge_time=%d sec, begin_soc=%d, wrong_touches=%d, finish_flag=%d"; /* ROM 0x6d6830 */
static const char aging_result_c[] = "[pt_protocol_procsr]Aging result: total_times=%d, total_time=%d sec, discharge_time=%d sec, begin_soc=%d, wrong_touches=%d, finish_flag=%d"; /* ROM 0x6d4540 */

/* get_device_id */
static const char fn_device_id[] = "get_device_id"; /* ROM 0x788570 */
static const char device_id_join[] = "join in get_device_id"; /* ROM 0x77ae94 */
static const char device_id_join_c[] = "[pt_protocol_procsr]join in get_device_id"; /* ROM 0x742338 */
static const char apb_fail[] = "get_device_id: apb510_get_chip_id failed, r=%d"; /* ROM 0x7375d4 */
static const char apb_fail_c[] = "[pt_protocol_procsr]get_device_id: apb510_get_chip_id failed, r=%d"; /* ROM 0x704d20 */
static const char apb_id[] = "get_device_id: apb_id=0x%08X"; /* ROM 0x764470 */
static const char apb_id_c[] = "[pt_protocol_procsr]get_device_id: apb_id=0x%08X"; /* ROM 0x72c750 */
static const char flash_fail[] = "get_device_id: mx25u25643g_get_device_id failed, r=%d"; /* ROM 0x721cf8 */
static const char flash_fail_c[] = "[pt_protocol_procsr]get_device_id: mx25u25643g_get_device_id failed, r=%d"; /* ROM 0x6f5904 */
static const char flash_id[] = "get_device_id: flash_id=0x%06X"; /* ROM 0x764490 */
static const char flash_id_c[] = "[pt_protocol_procsr]get_device_id: flash_id=0x%06X"; /* ROM 0x72c784 */
static const char npmx_fail[] = "get_device_id: npmx_get_device_id failed, r=%d"; /* ROM 0x737604 */
static const char npmx_fail_c[] = "[pt_protocol_procsr]get_device_id: npmx_get_device_id failed, r=%d"; /* ROM 0x704d64 */
static const char npmx_id[] = "get_device_id: npmx_id=0x%02X"; /* ROM 0x7644b0 */
static const char npmx_id_c[] = "[pt_protocol_procsr]get_device_id: npmx_id=0x%02X"; /* ROM 0x72c7b8 */
static const char imu_id[] = "get_device_id: imu_id=0x%08X"; /* ROM 0x7644d0 */
static const char imu_id_c[] = "[pt_protocol_procsr]get_device_id: imu_id=0x%08X"; /* ROM 0x72c7ec */
static const char imu_fail[] = "get_device_id: DRV_IMUReadWhoAmI failed, r=%d"; /* ROM 0x737634 */
static const char imu_fail_c[] = "[pt_protocol_procsr]get_device_id: DRV_IMUReadWhoAmI failed, r=%d"; /* ROM 0x704da8 */
static const char mag_id[] = "get_device_id: mag_id=0x%08X"; /* ROM 0x7644f0 */
static const char mag_id_c[] = "[pt_protocol_procsr]get_device_id: mag_id=0x%08X"; /* ROM 0x72c820 */
static const char mag_fail[] = "get_device_id: DRV_MAGReadWhoAmI failed, r=%d"; /* ROM 0x737664 */
static const char mag_fail_c[] = "[pt_protocol_procsr]get_device_id: DRV_MAGReadWhoAmI failed, r=%d"; /* ROM 0x704dec */
static const char panel_id[] = "get_device_id: panel_id=0x%04X"; /* ROM 0x764510 */
static const char panel_id_c[] = "[pt_protocol_procsr]get_device_id: panel_id=0x%04X"; /* ROM 0x72c854 */
static const char als_id[] = "get_device_id: als_id=0x%08X (man=0x%04X,did=0x%04X)"; /* ROM 0x721d30 */
static const char als_id_c[] = "[pt_protocol_procsr]get_device_id: als_id=0x%08X (man=0x%04X,did=0x%04X)"; /* ROM 0x6f5950 */
static const char touch_id[] = "get_device_id: touch_version=%d.%d.%d.%d"; /* ROM 0x742364 */
static const char touch_id_c[] = "[pt_protocol_procsr]get_device_id: touch_version=%d.%d.%d.%d"; /* ROM 0x70e364 */

/* get_firmware_version */
static const char fn_fw_version[] = "get_firmware_version"; /* ROM 0x77aeac */
static const char fw_join[] = "join in get_firmware_version"; /* ROM 0x764530 */
static const char fw_join_c[] = "[pt_protocol_procsr]join in get_firmware_version"; /* ROM 0x72c888 */
static const char fw_touch[] = "get_firmware_version: touch_version=%d.%d.%d.%d"; /* ROM 0x737694 */
static const char fw_touch_c[] = "[pt_protocol_procsr]get_firmware_version: touch_version=%d.%d.%d.%d"; /* ROM 0x704e30 */
static const char fw_codec[] = "get_firmware_version: codec_version=%d.%d.%d.%d"; /* ROM 0x7376c4 */
static const char fw_codec_c[] = "[pt_protocol_procsr]get_firmware_version: codec_version=%d.%d.%d.%d"; /* ROM 0x704e74 */
static const char fw_ble[] = "get_firmware_version: ble_fw_image_bin_ver=0x%08X"; /* ROM 0x72c8bc */
static const char fw_ble_c[] = "[pt_protocol_procsr]get_firmware_version: ble_fw_image_bin_ver=0x%08X"; /* ROM 0x6fc584 */

/* get_device_sync_status / set_mic_delay_1bit */
static const char fn_sync_status[] = "get_device_sync_status"; /* ROM 0x77aec4 */
static const char sync_status_join[] = "join in get_device_sync_status"; /* ROM 0x764550 */
static const char sync_status_join_c[] = "[pt_protocol_procsr]join in get_device_sync_status"; /* ROM 0x72c8f0 */
static const char fn_mic_delay[] = "set_mic_delay_1bit"; /* ROM 0x782ccc */
static const char mic_delay_join[] = "join in set_mic_delay_1bit"; /* ROM 0x7706d0 */
static const char mic_delay_join_c[] = "[pt_protocol_procsr]join in set_mic_delay_1bit"; /* ROM 0x7376f4 */

/* pt_ota_transmit_* */
static const char fn_ota_start[] = "pt_ota_transmit_start"; /* ROM 0x77aedc */
static const char ota_start_join[] = "join in pt_ota_transmit_start"; /* ROM 0x764570 */
static const char ota_start_join_c[] = "[pt_protocol_procsr]join in pt_ota_transmit_start"; /* ROM 0x72c924 */
static const char fn_ota_info[] = "pt_ota_transmit_information"; /* ROM 0x7706ec */
static const char ota_info_join[] = "join in pt_ota_transmit_information"; /* ROM 0x758c10 */
static const char ota_info_join_c[] = "[pt_protocol_procsr]join in pt_ota_transmit_information"; /* ROM 0x721d68 */
static const char ota_info_len[] = "pt_ota_transmit_information: data_len != EVEN_OTA_FILE_HEADER_SIZE, data_len=%d"; /* ROM 0x6ef4f8 */
static const char ota_info_len_c[] = "[pt_protocol_procsr]pt_ota_transmit_information: data_len != EVEN_OTA_FILE_HEADER_SIZE, data_len=%d"; /* ROM 0x6db7a4 */
static const char ota_info_nomem[] = "pt_ota_transmit_information: malloc failed"; /* ROM 0x742390 */
static const char ota_info_nomem_c[] = "[pt_protocol_procsr]pt_ota_transmit_information: malloc failed"; /* ROM 0x70e3a4 */
static const char fn_ota_file[] = "pt_ota_transmit_file"; /* ROM 0x77aef4 */
static const char ota_file_seq[] = "timestamp = %d, upgrade_file_timestamp = %d, is_last_packet = %d"; /* ROM 0x704eb8 */
static const char ota_file_seq_c[] = "[pt_protocol_procsr]timestamp = %d, upgrade_file_timestamp = %d, is_last_packet = %d"; /* ROM 0x6e4a08 */
static const char ota_file_ts[] = "pt_ota_transmit_file: timestamp is not equal to upgrade_file_timestamp, timestamp=%d, upgrade_file_timestamp=%d"; /* ROM 0x6d7580 */
static const char ota_file_ts_c[] = "[pt_protocol_procsr]pt_ota_transmit_file: timestamp is not equal to upgrade_file_timestamp, timestamp=%d, upgrade_file_timestamp=%d"; /* ROM 0x6d5150 */
static const char ota_file_crc[] = "pt_ota_transmit_file: crcCheck is not equal to recv_value[payload_len + 5], crcCheck = 0x%x, crc_pc = 0x%x"; /* ROM 0x6d7ccc */
static const char ota_file_crc_c[] = "[pt_protocol_procsr]pt_ota_transmit_file: crcCheck is not equal to recv_value[payload_len + 5], crcCheck = 0x%x, crc_pc = 0x%x"; /* ROM 0x6d5858 */
static const char ota_file_len[] = "pt_ota_transmit_file: payload_len is not equal to 1000, payload_len=%d"; /* ROM 0x6fc5cc */
static const char ota_file_len_c[] = "[pt_protocol_procsr]pt_ota_transmit_file: payload_len is not equal to 1000, payload_len=%d"; /* ROM 0x6e1544 */
static const char fn_ota_result[] = "pt_ota_transmit_result_check"; /* ROM 0x764590 */
static const char ota_result_join[] = "join in pt_ota_transmit_result_check"; /* ROM 0x74d4e4 */
static const char ota_result_join_c[] = "[pt_protocol_procsr]join in pt_ota_transmit_result_check"; /* ROM 0x717ed8 */
static const char ota_result[] = "pt_ota_transmit_result_check: g_production_ota_crc_result=%d"; /* ROM 0x70e3e4 */
static const char ota_result_c[] = "[pt_protocol_procsr]pt_ota_transmit_result_check: g_production_ota_crc_result=%d"; /* ROM 0x6e9754 */

static const char mode_write[] = "w"; /* ROM 0x57301c, inline literal */
static const char mode_read[] = "r";  /* ROM 0x573020, inline literal */

/* Peer sync request copied from ROM 0x78bd68 (12 bytes); bytes 4 and 5 are
 * replaced by the own and expected peer role. */
static const uint8_t peer_sync_template[12] = {
    0x03u, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x53u, 0x45u, 0x00u, 0x20u,
};

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Compressed-log word: level in bits 26+, argument count in bits 22+. */
#define PT_CLOG(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define PT_LOG0(level, fn, line, fmt, cfmt) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt)); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), 0), (cfmt), (cfmt)); \
    } while (0)
#define PT_LOGN(level, nargs, fn, line, fmt, cfmt, ...) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), __VA_ARGS__); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), (nargs)), (cfmt), (cfmt), __VA_ARGS__); \
    } while (0)
#define PT_PARA_NULL(fn, line) PT_LOGN(1, 1, (fn), (line), para_null, para_null_c, (fn))
#define PT_DENIED(fn, line) PT_LOG0(1, (fn), (line), denied, denied_c)
#define PT_BAD_ARGS(payload, length, rsp, rsp_len, min) \
    ((rsp) == NULL || (rsp_len) == NULL || (payload) == NULL || (uint8_t)(length) < (min))

/* Stock writes the response header inline with a running uint8_t index. */
#define PT_HEADER(rsp, idx, rsp_cmd, type, data_len) do { \
        (rsp)[(idx)++] = (rsp_cmd); \
        (rsp)[(idx)++] = 1u; \
        (rsp)[(idx)++] = (type); \
        (rsp)[(idx)++] = (data_len); \
    } while (0)

static void put_le32(uint8_t *rsp, uint8_t *idx, uint32_t value)
{
    rsp[(*idx)++] = (uint8_t)value;
    rsp[(*idx)++] = (uint8_t)(value >> 8);
    rsp[(*idx)++] = (uint8_t)(value >> 16);
    rsp[(*idx)++] = (uint8_t)(value >> 24);
}

/* Shared one-byte result frame [cmd][1][type][1][result]. */
int32_t pt_handler_result(uint8_t rsp_cmd, uint8_t result, uint8_t type, uint8_t *rsp, uint8_t *rsp_len)
{
    if (rsp == NULL || rsp_len == NULL)
        return -1;
    rsp[0] = rsp_cmd;
    rsp[1] = 1u;
    rsp[2] = type;
    rsp[3] = 1u;
    rsp[4] = result;
    *rsp_len = 5u;
    return 0;
}

/* cmd 0x35 get_flash_burn_info: write/read-back test of "boot_count" (status 1
 * open failure, 2 short or mismatching transfer), then check that the four
 * firmware images exist. The ack sent is 0 only when both pass. */
uint32_t pt_cmd_2A_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_flash_burn, 0x838u, flash_join, flash_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_flash_burn, 0x83bu);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x35u, 3u, 1u);

    uint8_t fs_status = 0;
    uint32_t read_back = 0;
    uint32_t pattern = 1;
    uint8_t size = 4;
    void *file = file_open(path_boot_count, mode_write);
    if (file == NULL) {
        fs_status = 1;
    } else {
        uint8_t written = (uint8_t)file_write(&pattern, 1u, size, file);
        (void)file_close(file);
        if (written != size) {
            fs_status = 2;
            PT_LOGN(1, 2, fn_flash_burn, 0x85au, fs_write_fail, fs_write_fail_c, size, written);
        } else {
            file = file_open(path_boot_count, mode_read);
            if (file == NULL) {
                fs_status = 1;
            } else {
                uint8_t got = (uint8_t)file_read(&read_back, 1u, size, file);
                (void)file_close(file);
                if (got != size || read_back != pattern) {
                    fs_status = 2;
                    /* Stock passes two arguments for the three conversions. */
                    PT_LOGN(1, 2, fn_flash_burn, 0x86du, fs_read_fail, fs_read_fail_c, size, got);
                }
            }
        }
    }
    rsp[4] = fs_status;

    bool ble = false, box = false, codec = false, touch = false;
    file = file_open(path_ble, mode_read);
    if (file != NULL) {
        ble = true;
        (void)file_close(file);
    }
    file = file_open(path_box, mode_read);
    if (file != NULL) {
        box = true;
        (void)file_close(file);
    }
    file = file_open(path_codec, mode_read);
    if (file != NULL) {
        codec = true;
        (void)file_close(file);
    }
    file = file_open(path_touch, mode_read);
    if (file != NULL) {
        touch = true;
        (void)file_close(file);
    }
    uint8_t ack;
    if (ble && box && codec && touch && fs_status == 0u) {
        rsp[4] = 0;
        ack = 0;
    } else {
        ack = 1;
        rsp[4] = 1;
    }
    PT_LOGN(3, 5, fn_flash_burn, 0x897u, files_check, files_check_c, ble, box, codec, touch, ack);
    PT_LOGN(3, 1, fn_flash_burn, 0x89au, flash_ack, flash_ack_c, ack);
    *rsp_len = 5u;
    return 0;
}

/* cmd 0x43 get_sync_status: send "ptSync" (7 bytes with NUL) over the sync UART
 * and poll up to 40 ticks for the echo the UART thread stores at
 * g2_uart_command+1 (it clears byte 0 when a reply arrives). */
uint32_t pt_cmd_31_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_sync, 0x8a4u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x43u, 3u, 1u);
    g2_uart_command[0] = 1u;
    (void)aeabi_memset_43c0e4(&g2_uart_command[1], 7u, 0);
    (void)audio_uart_sync_send(sync_token, 7u, 0u);
    uint8_t polls = PT_SYNC_POLLS;
    for (; polls != 0u; polls--) {
        (void)osDelay(1u);
        if (g2_uart_command[0] == 0u) {
            PT_LOGN(1, 1, fn_sync, 0x8beu, sync_rcv, sync_rcv_c, &g2_uart_command[1]);
            rsp[idx++] = g2_lfs_memcmp(&g2_uart_command[1], sync_token, 7u) == 0 ? 0u : 1u;
            break;
        }
    }
    if (polls == 0u) {
        PT_LOG0(1, fn_sync, 0x8cdu, sync_timeout, sync_timeout_c);
        rsp[idx++] = 1u;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x06 enter_ship_mode: acknowledge and leave the ship-mode entry to the
 * device manager (g2_dev_shipmode_pending). */
uint32_t pt_cmd_35_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_ship, 0x8d7u, ship_join, ship_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_ship, 0x8dau);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x06u, 3u, 1u);
    rsp[idx++] = 0u;
    g2_dev_shipmode_pending = 1u;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x1C set_device_sn_info: payload[4..17] is the 14-character PSN. It is
 * written to OTP and nvSysDt, then read back (status 1 on mismatch). */
uint32_t pt_cmd_38_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_sn_set, 0x8efu, sn_set_join, sn_set_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn_sn_set, 0x8f2u);
        return UINT32_MAX;
    }
    const char *psn = (const char *)&payload[4];
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x1cu, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        PT_LOGN(3, 2, fn_sn_set, 0x902u, sn_string, sn_string_c, psn, 14);
        (void)SVC_WritePSNToOTP(psn);
        (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_PSN, psn);
        rsp[idx++] = g2_lfs_memcmp(psn, SVC_NvdbReadSysData(G2_NVDB_SYSDT_PSN), 14u) == 0 ? 0u : 1u;
    } else {
        PT_DENIED(fn_sn_set, 0x914u);
        rsp[idx++] = 5u;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x22 get_device_sn_info: data is the stored PSN, at most 14 bytes. */
uint32_t pt_cmd_39_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_sn_get, 0x91eu, sn_get_join, sn_get_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_sn_get, 0x921u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    rsp[idx++] = 0x22u;
    rsp[idx++] = 1u;
    rsp[idx++] = 3u;
    const char *psn = (const char *)display_driver_brightness_ratio_cell_4af73a(G2_NVDB_SYSDT_PSN);
    uint8_t n = g2_log_module_length(psn) < 15u ? (uint8_t)g2_log_module_length(psn) : 14u;
    rsp[idx++] = n;
    (void)audio_queue_copy_bytes(&rsp[idx], psn, n);
    *rsp_len = (uint8_t)(n + idx);
    return 0;
}

/* cmd 0x3E set_aging_test_info (type 2): payload[4] = 1 starts, 0 stops the
 * aging test. Starting records the RTC time in nvSysDt.aging_start, bumps
 * aging_total_times and starts the 0x104 display app on the peer; stopping
 * records aging_end, sets aging_finish_flag and stops the app. The active flag
 * is only set here (the stop path leaves it for the aging test owner). A start
 * while running re-applies panel brightness 100 and answers data 00 04. */
uint32_t pt_cmd_3E_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_aging_set, 0x9acu, aging_set_join, aging_set_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_aging_set, 0x9afu);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x3eu, 2u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        rsp[idx++] = 0u;
        if (payload[4] == 1u) {
            if (g2_pdm_production_bypass == 1u) {
                PT_LOG0(3, fn_aging_set, 0x9c2u, aging_running, aging_running_c);
                rsp[idx++] = 4u;
                (void)display_driver_case4_apply(100u, 0x1bbcu, 0x3fu);
                *rsp_len = idx;
                return 0;
            }
            PT_LOG0(3, fn_aging_set, 0x9cau, aging_enter, aging_enter_c);
            g2_pdm_production_bypass = 1u;
            nvdbSysDtResetAging();
            SVC_SystemTimeSync(g2_kvdb_time_record.timestamp, g2_kvdb_time_record.timezone);
            (void)audio_uart_slave_display_start(PT_AGING_DISPLAY_APP, NULL, 0u);
            g2_nvdb_aging_time_t now;
            service_time_current_calendar_get(&now);
            (void)aeabi_memcpy4_439c04(&SYS_DT->aging_start, &now, sizeof(now));
            SYS_DT->aging_total_times++;
            (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_AGING_START, &SYS_DT->aging_start);
        } else if (payload[4] == 0u) {
            if (g2_pdm_production_bypass == 0u) {
                PT_LOG0(3, fn_aging_set, 0x9dfu, aging_idle, aging_idle_c);
                rsp[idx++] = 4u;
                *rsp_len = idx;
                return 0;
            }
            PT_LOG0(3, fn_aging_set, 0x9e6u, aging_exit, aging_exit_c);
            (void)audio_uart_slave_display_stop(PT_AGING_DISPLAY_APP, NULL, 0u);
            g2_nvdb_aging_time_t now;
            service_time_current_calendar_get(&now);
            SYS_DT->aging_finish_flag = 1u;
            (void)aeabi_memcpy4_439c04(&SYS_DT->aging_end, &now, sizeof(now));
            (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_AGING_END, &SYS_DT->aging_end);
        }
    } else {
        PT_DENIED(fn_aging_set, 0x9f3u);
        rsp[idx++] = 5u;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x44 set_buzzer_status: payload[4] = 1 starts a 4 kHz, 30 % tone, 0 stops
 * it, anything else answers status 1. */
uint32_t pt_cmd_42_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_buzzer, 0x9fdu, buzzer_join, buzzer_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_buzzer, 0xa00u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x44u, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        if (payload[4] == 1u) {
            PT_LOG0(3, fn_buzzer, 0xa10u, buzzer_open, buzzer_open_c);
            DRV_BuzzerStart(4000u, 30u);
            rsp[idx++] = 0u;
        } else if (payload[4] == 0u) {
            PT_LOG0(3, fn_buzzer, 0xa17u, buzzer_close, buzzer_close_c);
            DRV_BuzzerStop();
            rsp[idx++] = 0u;
        } else {
            PT_LOG0(1, fn_buzzer, 0xa1du, buzzer_error, buzzer_error_c);
            rsp[idx++] = 1u;
        }
    } else {
        PT_DENIED(fn_buzzer, 0xa23u);
        rsp[idx++] = 5u;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x46 get_aging_mode_info (type 2): 1 while the aging test is active. */
uint32_t pt_cmd_44_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_aging_mode, 0xa7du, aging_mode_join, aging_mode_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_aging_mode, 0xa80u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x46u, 2u, 1u);
    rsp[idx++] = g2_pdm_production_bypass != 0u ? 1u : 0u;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x3D get_aging_result_info: 12 data bytes, total_times, total and
 * discharge seconds (end - start and soc_to_10 - start, LE32), begin SoC,
 * wrong touches, finish flag. */
uint32_t pt_cmd_46_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_aging_result, 0xa93u, aging_result_join, aging_result_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_aging_result, 0xa96u);
        return UINT32_MAX;
    }
    g2_nvdb_sys_dt_t *sys = SYS_DT;
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x3du, 3u, 12u);
    rsp[idx++] = sys->aging_total_times;
    int32_t total = calculate_rtc_time_diff_seconds_56f178(&sys->aging_end, &sys->aging_start);
    put_le32(rsp, &idx, (uint32_t)total);
    int32_t discharge = calculate_rtc_time_diff_seconds_56f178(&sys->aging_soc_to_10, &sys->aging_start);
    put_le32(rsp, &idx, (uint32_t)discharge);
    rsp[idx++] = sys->aging_begin_charge_soc;
    rsp[idx++] = sys->aging_wrong_touch_times;
    rsp[idx++] = sys->aging_finish_flag;
    PT_LOGN(3, 6, fn_aging_result, 0xabdu, aging_result, aging_result_c, sys->aging_total_times, total,
            discharge, sys->aging_begin_charge_soc, sys->aging_wrong_touch_times, sys->aging_finish_flag);
    *rsp_len = idx;
    return 0;
}

/* cmd 0x47 get_device_id: payload[4] selects the chip, data is its ID (LE32):
 * 0 Apollo510 chip ID, 1 MX25U25643G JEDEC ID (3 bytes), 2 nPM1300 ID (1 byte),
 * 3 IMU WHO_AM_I, 4 magnetometer WHO_AM_I, 5 panel chip ID (2 bytes),
 * 6 OPT3007 manufacturer | device ID << 16 (powers the sensor rail first),
 * 7 touch firmware version bytes. Errors are logged; the ID is sent anyway. */
uint32_t pt_cmd_47_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_device_id, 0xac5u, device_id_join, device_id_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn_device_id, 0xac8u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x47u, 3u, 4u);
    int32_t r;
    switch (payload[4]) {
    case 0: {
        uint32_t id = 0;
        r = input_tick_read(&id);
        if (r != 0)
            PT_LOGN(1, 1, fn_device_id, 0xadcu, apb_fail, apb_fail_c, r);
        PT_LOGN(3, 1, fn_device_id, 0xadeu, apb_id, apb_id_c, id);
        put_le32(rsp, &idx, id);
        break;
    }
    case 1: {
        uint32_t id = 0;
        r = mx25u25643g_get_device_id_4700b4(&id);
        if (r != 0)
            PT_LOGN(1, 1, fn_device_id, 0xaecu, flash_fail, flash_fail_c, r);
        PT_LOGN(3, 1, fn_device_id, 0xaeeu, flash_id, flash_id_c, id);
        rsp[idx++] = (uint8_t)id;
        rsp[idx++] = (uint8_t)(id >> 8);
        rsp[idx++] = (uint8_t)(id >> 16);
        rsp[idx++] = 0u;
        break;
    }
    case 2: {
        uint32_t id = 0;
        r = npmx_get_device_id_512b20(&id);
        if (r != 0)
            PT_LOGN(1, 1, fn_device_id, 0xafbu, npmx_fail, npmx_fail_c, r);
        PT_LOGN(3, 1, fn_device_id, 0xafeu, npmx_id, npmx_id_c, id & 0xffu);
        rsp[idx++] = (uint8_t)id;
        rsp[idx++] = 0u;
        rsp[idx++] = 0u;
        rsp[idx++] = 0u;
        break;
    }
    case 3: {
        uint32_t id = 0;
        r = DRV_IMUReadWhoAmI(&id);
        PT_LOGN(3, 1, fn_device_id, 0xb0au, imu_id, imu_id_c, id);
        if (r != 0)
            PT_LOGN(1, 1, fn_device_id, 0xb0du, imu_fail, imu_fail_c, r);
        put_le32(rsp, &idx, id);
        break;
    }
    case 4: {
        uint32_t id = 0;
        r = DRV_MAGReadWhoAmI(&id);
        PT_LOGN(3, 1, fn_device_id, 0xb1au, mag_id, mag_id_c, id);
        if (r != 0)
            PT_LOGN(1, 1, fn_device_id, 0xb1du, mag_fail, mag_fail_c, r);
        put_le32(rsp, &idx, id);
        break;
    }
    case 5: {
        uint32_t id = uled_safe_get_chip_id();
        PT_LOGN(3, 1, fn_device_id, 0xb29u, panel_id, panel_id_c, id & 0xffffu);
        rsp[idx++] = (uint8_t)id;
        rsp[idx++] = (uint8_t)(id >> 8);
        rsp[idx++] = 0u;
        rsp[idx++] = 0u;
        break;
    }
    case 6: {
        g2_opt3007_regmap_t map;
        pt_sensor_rail_power_on_58f936();
        ti_opt3007_assignRegistermap(&map);
        opt3007_mode_continuous_set_58f8cc(&map);
        opt3007_conversion_100ms_set_58f8d8(&map);
        uint16_t man = opt3007_manufacturer_id_get_58f922(&map);
        uint32_t did = opt3007_device_id_get_58f92c(&map);
        uint32_t id = (uint32_t)man | (did << 16);
        PT_LOGN(3, 3, fn_device_id, 0xb43u, als_id, als_id_c, id, (uint32_t)man, did & 0xffffu);
        rsp[idx++] = (uint8_t)man;
        rsp[idx++] = (uint8_t)(man >> 8);
        rsp[idx++] = (uint8_t)did;
        rsp[idx++] = (uint8_t)(did >> 8);
        break;
    }
    case 7: {
        const uint8_t *v = g2_touch_version_bytes;
        PT_LOGN(3, 4, fn_device_id, 0xb4du, touch_id, touch_id_c, v[0], v[1], v[2], v[3]);
        rsp[idx++] = v[0];
        rsp[idx++] = v[1];
        rsp[idx++] = v[2];
        rsp[idx++] = v[3];
        break;
    }
    default: {
        /* Stock rewrites the frame as 48 01 03 01 03 with a fresh index but
         * still reports rsp_len 4. */
        uint8_t e = 0;
        rsp[e++] = 0x48u;
        rsp[e++] = 1u;
        rsp[e++] = 3u;
        rsp[e++] = 1u;
        rsp[e++] = 3u;
        break;
    }
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x48 get_firmware_version: payload[4] 0 = touch, 1 = GX8002 codec (both
 * 4 version bytes), 2 = BLE image version (LE32); others answer status 3 with
 * rsp_len 4 as in get_device_id. */
uint32_t pt_cmd_48_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_fw_version, 0xb65u, fw_join, fw_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn_fw_version, 0xb68u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x48u, 3u, 4u);
    switch (payload[4]) {
    case 0: {
        const uint8_t *v = g2_touch_version_bytes;
        PT_LOGN(3, 4, fn_fw_version, 0xb78u, fw_touch, fw_touch_c, v[0], v[1], v[2], v[3]);
        rsp[idx++] = v[0];
        rsp[idx++] = v[1];
        rsp[idx++] = v[2];
        rsp[idx++] = v[3];
        break;
    }
    case 1: {
        const uint8_t *v = g2_gx8002_version;
        rsp[idx++] = v[0];
        rsp[idx++] = v[1];
        rsp[idx++] = v[2];
        rsp[idx++] = v[3];
        PT_LOGN(3, 4, fn_fw_version, 0xb86u, fw_codec, fw_codec_c, v[0], v[1], v[2], v[3]);
        break;
    }
    case 2: {
        uint32_t version = audio_ble_hci_radio_revision_52dee6();
        PT_LOGN(3, 1, fn_fw_version, 0xb8du, fw_ble, fw_ble_c, version);
        put_le32(rsp, &idx, version);
        break;
    }
    default: {
        uint8_t e = 0;
        rsp[e++] = 0x48u;
        rsp[e++] = 1u;
        rsp[e++] = 3u;
        rsp[e++] = 1u;
        rsp[e++] = 3u;
        break;
    }
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x49 get_device_sync_status: send the 12-byte sync request (app 0x102)
 * with the own role and the expected peer role (1 <-> 2) to the other arm and
 * wait 20 ticks; status 0 when the peer acknowledged. */
uint32_t pt_cmd_49_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_sync_status, 0xba5u, sync_status_join, sync_status_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_sync_status, 0xba8u);
        return UINT32_MAX;
    }
    g2_pt_peer_sync_ack_20075004 = 0u;
    uint32_t request[3];
    (void)audio_queue_copy_bytes(request, peer_sync_template, sizeof(request));
    uint8_t *bytes = (uint8_t *)request;
    bytes[4] = (uint8_t)display_driver_uled_mode_45a568();
    bytes[5] = display_driver_uled_mode_45a568() == 1u ? 2u : 1u;
    (void)audio_uart_request_send(PT_PEER_SYNC_APP, request, sizeof(request), 0u);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x49u, 3u, 1u);
    (void)osDelay(20u);
    rsp[idx++] = g2_pt_peer_sync_ack_20075004 != 0u ? 0u : 1u;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x57 set_mic_delay_1bit: no NULL-argument log in stock. */
uint32_t pt_cmd_57_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_mic_delay, 0xbceu, mic_delay_join, mic_delay_join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 4u)
        return UINT32_MAX;
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x57u, 3u, 1u);
    (void)SVC_CodecMicDelay1Bit();
    rsp[idx++] = 0u;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x52 pt_ota_transmit_start: select the production OTA interface, reset
 * the packet sequence and RAM gather buffer, send OTA frame 0x00 (start) and
 * raise the caller's thread to priority 47 (osPriorityHigh7). */
uint32_t pt_cmd_52_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_ota_start, 0xbf5u, ota_start_join, ota_start_join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 4u)
        return UINT32_MAX;
    OTA_SetInterface(1u);
    g2_pt_ota_sequence_20075005 = 0u;
    g2_dev_status_pin_inhibit = 1u;
    g2_pt_ota_rx_fill_200748dc = 0u;
    uint8_t stage;
    (void)aeabi_memset_43c0e4(&stage, 1u, 0);
    (void)semantic_OtaFrameDispatch(PT_OTA_FRAME_COMMAND, &stage, 1u);
    (void)osThreadSetPriority(osThreadGetId(), 0x2f);
    return pt_handler_result(0x52u, 0u, 3u, rsp, rsp_len);
}

/* cmd 0x53 pt_ota_transmit_information: payload[3] must be 0x80; the 128-byte
 * OTA file header at payload[4] goes out as OTA frame 0x01 + header, followed
 * by frame 0x02. Status 1 out of memory, 3 wrong length. */
uint32_t pt_cmd_53_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_ota_info, 0xc0eu, ota_info_join, ota_info_join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 0x80u)
        return UINT32_MAX;
    uint8_t data_len = payload[3];
    if (data_len != PT_OTA_HEADER_SIZE) {
        PT_LOGN(1, 1, fn_ota_info, 0xc15u, ota_info_len, ota_info_len_c, data_len);
        return pt_handler_result(0x53u, 3u, 3u, rsp, rsp_len);
    }
    uint8_t *frame = file_heap_allocate(PT_OTA_HEADER_SIZE + 1u);
    if (frame == NULL) {
        PT_LOG0(1, fn_ota_info, 0xc1du, ota_info_nomem, ota_info_nomem_c);
        return pt_handler_result(0x53u, 1u, 3u, rsp, rsp_len);
    }
    frame[0] = 1u;
    (void)audio_queue_copy_bytes(&frame[1], &payload[4], PT_OTA_HEADER_SIZE);
    (void)semantic_OtaFrameDispatch(PT_OTA_FRAME_COMMAND, frame, PT_OTA_HEADER_SIZE + 1u);
    file_heap_free(frame);
    uint8_t stage = 2u;
    (void)semantic_OtaFrameDispatch(PT_OTA_FRAME_COMMAND, &stage, 1u);
    return pt_handler_result(0x53u, 0u, 3u, rsp, rsp_len);
}

/* cmd 0x54 pt_ota_transmit_file: payload[3..4] = packet length (LE16, data +
 * 4), payload[5] = last-packet flag, payload[6] = sequence, data at payload[7]
 * followed by its CRC16 (0x49acd4, no seed). Only full 1000-byte packets or
 * the last packet are accepted. A repeat of the previous sequence is acked
 * without storing. */
uint32_t pt_cmd_54_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 4u)
        return UINT32_MAX;
    uint16_t packet_len = (uint16_t)(payload[3] | ((uint32_t)payload[4] << 8));
    bool is_last = payload[5] != 0u;
    uint8_t seq = payload[6];
    PT_LOGN(4, 3, fn_ota_file, 0xc3au, ota_file_seq, ota_file_seq_c, seq, g2_pt_ota_sequence_20075005, is_last);
    if (seq == g2_pt_ota_sequence_20075005) {
        int32_t n = packet_len < 3u ? 0 : (int32_t)packet_len - 4;
        const uint8_t *data = &payload[7];
        uint16_t crc_pc = (uint16_t)(data[n] | ((uint32_t)data[n + 1] << 8));
        uint16_t crc = audio_uart_hand_checksum_49acd4(data, (uint32_t)n, NULL);
        if (crc != crc_pc) {
            PT_LOGN(1, 2, fn_ota_file, 0xc4du, ota_file_crc, ota_file_crc_c, crc, crc_pc);
            return pt_handler_result(0x54u, 1u, 3u, rsp, rsp_len);
        }
        if (!is_last && n != PT_OTA_PACKET_SIZE) {
            PT_LOGN(1, 1, fn_ota_file, 0xc53u, ota_file_len, ota_file_len_c, n);
            return pt_handler_result(0x54u, 1u, 3u, rsp, rsp_len);
        }
        if (n != 0) {
            g2_pt_ota_sequence_20075005 = (uint8_t)(seq + 1u);
            (void)audio_queue_copy_bytes(&g2_pt_ota_rx_buffer_20058388[g2_pt_ota_rx_fill_200748dc], data, (uint32_t)n);
            g2_pt_ota_rx_fill_200748dc += (uint32_t)n;
        }
        if (g2_pt_ota_rx_fill_200748dc > PT_OTA_FLUSH_THRESHOLD || is_last) {
            (void)audio_queue_copy_bytes(g2_pt_ota_frame_buffer, g2_pt_ota_rx_buffer_20058388,
                                         g2_pt_ota_rx_fill_200748dc);
            g2_pt_ota_frame_length = g2_pt_ota_rx_fill_200748dc;
            g2_pt_ota_frame_pending = 1u;
            g2_pt_ota_rx_fill_200748dc = 0u;
            (void)aeabi_memset_43c0e4(g2_pt_ota_rx_buffer_20058388, PT_OTA_RX_BUFFER_SIZE, 0);
        }
        return pt_handler_result(0x54u, 0u, 3u, rsp, rsp_len);
    }
    if (g2_pt_ota_sequence_20075005 == (uint32_t)((seq + 1) % 0x100)) {
        g2_pt_ota_sequence_20075005 = (uint8_t)(seq + 1u);
        return pt_handler_result(0x54u, 0u, 3u, rsp, rsp_len);
    }
    PT_LOGN(1, 2, fn_ota_file, 0xc40u, ota_file_ts, ota_file_ts_c, seq, g2_pt_ota_sequence_20075005);
    return pt_handler_result(0x54u, 1u, 3u, rsp, rsp_len);
}

/* cmd 0x55 pt_ota_transmit_result_check: send OTA frame 0x03 (finish) and
 * answer the CRC verdict of the OTA service. No argument checks in stock. */
uint32_t pt_cmd_55_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    (void)payload;
    (void)length;
    PT_LOG0(3, fn_ota_result, 0xc6fu, ota_result_join, ota_result_join_c);
    uint8_t stage = 3u;
    (void)semantic_OtaFrameDispatch(PT_OTA_FRAME_COMMAND, &stage, 1u);
    PT_LOGN(3, 1, fn_ota_result, 0xc72u, ota_result, ota_result_c, g2_ota_crc_failed);
    return pt_handler_result(0x55u, g2_ota_crc_failed, 3u, rsp, rsp_len);
}
