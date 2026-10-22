/* Product-test, PT protocol, device manager, board configuration and eAT
 * core storage (S3 storage-definition pass, 2.2.6.10).
 *
 * Stock owners: the PT protocol processor (a-55..a-58-pt-protocol), the
 * device manager (a-22-device-manager), the production mic / LC3 test
 * (p-09-product-test, ux_production_sync.c), the aging test page
 * (p-02-aging-test), board configuration (a-41-board-config) and
 * platform\service\eAT\core\at_core.c (a-46-at-core). .data values are from
 * the decoded startup init image (scatter record 0x75d3f4, RAM
 * 0x20000000..0x20004557); other RAM cells are zero-init
 * (0x20004558..0x20075048 or SSRAM). ROM objects are copied from
 * ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). */
#include <stdint.h>
#include "g2_at_core.h"
#include "g2_hal_gpio.h"

/* ---- a-22-device-manager ------------------------------------------------ */

/* RAM 0x20004545 (.data): 01, aging alert enabled. */
volatile uint8_t g2_dev_aging_alert_on = 1u;
volatile uint8_t g2_dev_shipmode_pending;   /* RAM 0x20075003 */
volatile uint8_t g2_dev_box_ota_mode;       /* RAM 0x20075009 g_is_box_ota_mode */
volatile uint8_t g2_dev_status_pin_inhibit; /* RAM 0x2007500a */
volatile uint32_t g2_dev_box_ota_start_s;   /* RAM 0x200748ec, seconds */
/* RAM 0x20073b18: charger telemetry record, 0x18 bytes (the device manager
 * and charger_common views are 0x18, the bq27427/bq25180/npmx views 0x14;
 * stride 0x18). */
__attribute__((aligned(4))) uint8_t g2_charger_telemetry[0x18];
/* RAM 0x20070f78: npmx_instance_t of the nPM1300 glue. sizeof(struct
 * npmx_instance) is 0xd0 for npmx e1aaec53 with the U8 NPM1300 config,
 * equal to the stock stride. */
__attribute__((aligned(4))) uint8_t g2_npmx_instance[0xd0];

/* ---- a-55..a-58 PT protocol --------------------------------------------- */

/* RAM 0x20004551 (.data): 01. */
volatile uint8_t g2_production_lc3_enable = 1u;
/* RAM 0x20004552 (.data): 01. */
volatile uint8_t g2_pt_font_crc_failed = 1u;
/* RAM 0x20058388 / 0x20059ef8 (SSRAM): OTA frame reassembly and the staged
 * copy forwarded by command 0x54, PT_OTA_RX_BUFFER_SIZE 0x1b70 each (stride
 * 0x1b70). */
__attribute__((aligned(4))) uint8_t g2_pt_ota_rx_buffer_20058388[0x1b70];
__attribute__((aligned(4))) uint8_t g2_pt_ota_frame_buffer[0x1b70];
uint32_t g2_pt_lux_gear1_200748c4;        /* RAM 0x200748c4 */
uint32_t g2_pt_lux_curve_a1_200748c8;     /* RAM 0x200748c8 */
uint32_t g2_pt_audio_last_chunk_200748cc; /* RAM 0x200748cc */
uint8_t *g2_pt_audio_file_cache_200748d0; /* RAM 0x200748d0 */
uint32_t g2_pt_audio_cache_size_200748d4; /* RAM 0x200748d4 */
uint32_t g2_pt_audio_cache_offset_200748d8; /* RAM 0x200748d8 */
uint32_t g2_pt_ota_rx_fill_200748dc;      /* RAM 0x200748dc */
volatile uint32_t g2_pt_ota_frame_length; /* RAM 0x200748e0 */
void *g2_pt_box_ota_file;                 /* RAM 0x200748e4 lfs_file_t * */
volatile uint32_t g2_pt_box_ota_crc;      /* RAM 0x200748e8 */
volatile uint8_t g2_pt_peer_sync_ack_20075004; /* RAM 0x20075004 */
uint8_t g2_pt_ota_sequence_20075005;      /* RAM 0x20075005 */
uint8_t g2_pt_audio_cache_valid_20075006; /* RAM 0x20075006 */
volatile uint8_t g2_pt_ota_frame_pending; /* RAM 0x20075008 */
char g2_pt_audio_cache_path_2007393c[0x20]; /* RAM 0x2007393c, PT_CACHE_PATH_SIZE */
uint8_t g2_touch_version_bytes[4];        /* RAM 0x20074508, last raw touch version reply */
uint8_t g2_gx8002_version[4];             /* RAM 0x20074940, last GX8002 version read */

/* ---- p-09-product-test -------------------------------------------------- */

volatile uint32_t g2_production_codec_mic_state; /* RAM 0x20074890 */
/* RAM 0x20004557 (.data): 55. */
uint8_t g2_production_sync_recv_data = 0x55u;
/* RAM 0x20106a7c / 0x201074c0 / 0x20107f04 (SSRAM): LC3 encoder records
 * (0x1c-byte header + encoder memory), stride 0xa44 each. */
__attribute__((aligned(4))) uint8_t g2_lc3_encoder_codec_left[0xa44];
__attribute__((aligned(4))) uint8_t g2_lc3_encoder_codec_right[0xa44];
__attribute__((aligned(4))) uint8_t g2_lc3_encoder_pdm[0xa44];

/* ---- p-02-aging-test ---------------------------------------------------- */

uint32_t g2_aging_test_rect;          /* RAM 0x2007411c lv_obj_t * */
int32_t g2_aging_test_rect_position;  /* RAM 0x200741b8, row 0..5 */
uint32_t g2_aging_test_page_root;     /* RAM 0x200741bc lv_obj_t * */
uint8_t g2_aging_test_event_count;    /* RAM 0x20074f4c */
uint8_t g2_aging_test_rect_ready;     /* RAM 0x20074f4d */

/* ---- a-41-board-config -------------------------------------------------- */

/* ROM 0x78ee8c: am_hal_gpio_pincfg_t 0x00000000 (ADC function). */
const uint32_t g2_board_hwid_pin_adc_cfg_78ee8c = 0x00000000u;
/* ROM 0x78ee90: am_hal_gpio_pincfg_t 0x00000003 (released). */
const uint32_t g2_board_hwid_pin_off_cfg_78ee90 = 0x00000003u;

/* GPIO IRQ handlers named in the table. 0x510fd8 (GPIO4, nPM1300 IRQ: emits
 * ring event 0 via 0x4ac16c) and 0x55ba64 (GPIO27, touch attention: calls
 * input_msg_send_touch 0x513056 with 0) are not yet written in g2/src. */
extern void board_gpio4_pmic_isr_510fd8(void);   /* 0x510fd8 */
extern void board_gpio27_touch_isr_55ba64(void); /* 0x55ba64 */
extern void gx8002_audio_thread_notify(void);    /* 0x57a80e */
extern void hub_als_timer_callback(void);        /* 0x4a6ae8 */
typedef void (*g2_gpio_handler_t)(void *);

/* ROM 0x686db8..0x687243: board pin table, 0x61 rows of
 * {pin, mode, level, int_dir, reserved, handler}. */
const g2_gpio_row_t g2_board_gpio_table_686db8[0x61] = {
    { 0u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    { 1u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    { 2u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    { 3u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    { 4u, 0x2u, 0x0u, 0x2u, 0x0u, (g2_gpio_handler_t)(void (*)(void))board_gpio4_pmic_isr_510fd8},
    { 5u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    { 6u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    { 7u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    { 8u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    { 9u, 0x1u, 0x1u, 0x0u, 0x0u, 0},
    {10u, 0x1u, 0x1u, 0x0u, 0x0u, 0},
    {11u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {12u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {13u, 0x2u, 0x0u, 0x0u, 0x0u, 0},
    {14u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {15u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {16u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {17u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {18u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {19u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {20u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {21u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {22u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {23u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {24u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {25u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {26u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {27u, 0x2u, 0x0u, 0x1u, 0x0u, (g2_gpio_handler_t)(void (*)(void))board_gpio27_touch_isr_55ba64},
    {28u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {29u, 0x2u, 0x1u, 0x1u, 0x0u, (g2_gpio_handler_t)(void (*)(void))gx8002_audio_thread_notify},
    {31u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {32u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {33u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {34u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {35u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {36u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {37u, 0x2u, 0x0u, 0x0u, 0x0u, 0},
    {38u, 0x2u, 0x0u, 0x2u, 0x0u, (g2_gpio_handler_t)(void (*)(void))hub_als_timer_callback},
    {39u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {40u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {41u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {42u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {43u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {44u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {45u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {46u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {47u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {48u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {49u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {50u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {51u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {57u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {64u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {65u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {66u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {67u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {68u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {69u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {70u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {71u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {72u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {73u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {83u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {84u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {85u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {86u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {87u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {88u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {95u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {96u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {97u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {98u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {99u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {100u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {101u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {102u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {103u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {104u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {125u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {126u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {127u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {128u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {129u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {134u, 0x1u, 0x1u, 0x0u, 0x0u, 0},
    {142u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {143u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {144u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {145u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {146u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {147u, 0x1u, 0x0u, 0x0u, 0x0u, 0},
    {156u, 0x2u, 0x0u, 0x0u, 0x0u, 0},
    {157u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {158u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {159u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {160u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
    {199u, 0x3u, 0x0u, 0x0u, 0x0u, 0},
    {200u, 0x4u, 0x0u, 0x0u, 0x0u, 0},
};

/* ---- a-46-at-core ------------------------------------------------------- */

/* RAM 0x2037bf5c (SSRAM): g2_at_core_t, 0x124 bytes. */
__attribute__((aligned(4))) uint8_t g2_at_core[0x124];
/* RAM 0x2037b3c0 (SSRAM): three 256-byte argument slots. */
char g2_at_core_args[3][0x100];
/* ROM 0x78f538: "=" (0x3d 0x00). */
const char g2_at_arg_delimiter[2] = "=";

/* Registered handlers, resolved by address. The one-argument handlers are
 * converted to the two-argument row type (the second argument is ignored). */
extern int32_t atCleanBondHandler(const char *param);       /* 0x5a4fa4 */
extern int32_t atBleKeepConnectHandler(const char *param);  /* 0x5a4fb4 */
extern int32_t _atBuzzerTest(const char *para1);            /* 0x5a4fd0 */
extern int32_t _atAudioCtrl(const char *arg1, const char *arg2); /* 0x5a5488 */
extern int32_t atNusHandler(const char *arg1, const char *arg2); /* 0x5a5520 */
extern int32_t _atRM(const char *arg1, const char *arg2);   /* 0x5a5530 */
extern int32_t atLsHandler(const char *arg1, const char *arg2); /* 0x5a567a */
extern int32_t atMkdirHandler(const char *arg1, const char *arg2); /* 0x5a56a0 */
extern int32_t atInfoHandler(const char *param);            /* 0x5a5720 */
extern int32_t atResetHandler(const char *param);           /* 0x5a57a4 */
extern int32_t atPsnHandler(const char *param);             /* 0x5a57f0 */
extern int32_t atImuRawDataHandler(const char *param);      /* 0x5a5830 */
extern int32_t atImuEulerHandler(const char *param);        /* 0x5a5864 */
extern int32_t atScreenXHandler(const char *param);         /* 0x5a58a8 */
extern int32_t atScreenYHandler(const char *param);         /* 0x5a58b4 */
extern int32_t atAlsReadHandler(const char *param);         /* 0x5a58d4 */
extern int32_t atAlsHandler(const char *param);             /* 0x5a58fa */
extern int32_t atBrightnessHandler(const char *param);      /* 0x5a5920 */
extern int32_t atAlsScaleReadHandler(const char *param);    /* 0x5a593a */
extern int32_t atBrightnessReadHandler(const char *param);  /* 0x5a594c */
extern int32_t _atTpTest(const char *arg1, const char *arg2); /* 0x5a5998 */

/* Generic function pointer step: the row type differs from the handler's. */
#define AT1(f) ((g2_at_handler_t)(void (*)(void))(f))

/* ROM 0x6c9260..0x6c93af: the stock linker-collected eAT registry, 21 rows
 * of {type, name, handler, 0}. g2_at_cmd_table_end (ROM 0x6c93b0) is an
 * assembler alias one past the last row. */
const g2_at_cmd_t g2_at_cmd_table_start[21] = {
    {0u, "AT^CLEANBOND", AT1(atCleanBondHandler), 0u},          /* name ROM 0x7850e0 */
    {1u, "AT^BLE_KEEPCONNECT", AT1(atBleKeepConnectHandler), 0u}, /* 0x77e17c */
    {2u, "AT^BUZZER", AT1(_atBuzzerTest), 0u},                  /* 0x78a334 */
    {0u, "AT^AUDIO", _atAudioCtrl, 0u},                         /* 0x78a34c */
    {0u, "AT^NUS", atNusHandler, 0u},                           /* 0x78cbc4 */
    {3u, "AT^RM", _atRM, 0u},                                   /* 0x78cbfc */
    {3u, "AT^LS", atLsHandler, 0u},                             /* 0x78cc04 */
    {3u, "AT^MKDIR", atMkdirHandler, 0u},                       /* 0x78a394 */
    {0u, "AT^INFO", AT1(atInfoHandler), 0u},                    /* 0x78cc14 */
    {0u, "AT^RESET", AT1(atResetHandler), 0u},                  /* 0x78a3dc */
    {0u, "AT^PSN", AT1(atPsnHandler), 0u},                      /* 0x78cc1c */
    {2u, "AT^IMU_RAWDATA", AT1(atImuRawDataHandler), 0u},       /* 0x785170 */
    {0u, "AT^IMU_EULER", AT1(atImuEulerHandler), 0u},           /* 0x785180 */
    {2u, "AT^SCRN_X", AT1(atScreenXHandler), 0u},               /* 0x78a3f4 */
    {2u, "AT^SCRN_Y", AT1(atScreenYHandler), 0u},               /* 0x78a400 */
    {0u, "AT^ALS_READ", AT1(atAlsReadHandler), 0u},             /* 0x78a40c */
    {0u, "AT^ALS", AT1(atAlsHandler), 0u},                      /* 0x78cc24 */
    {2u, "AT^BRIGHTNESS", AT1(atBrightnessHandler), 0u},        /* 0x7851b0 */
    {0u, "AT^ALS_SCALE_READ", AT1(atAlsScaleReadHandler), 0u},  /* 0x77e1b8 */
    {0u, "AT^BRIGHTNESS_READ", AT1(atBrightnessReadHandler), 0u}, /* 0x77e1cc */
    {0u, "AT^TP", _atTpTest, 0u},                               /* 0x78cc44 */
};
__asm__(".globl g2_at_cmd_table_end\n"
        ".set g2_at_cmd_table_end, g2_at_cmd_table_start + 0x150\n"
        ".type g2_at_cmd_table_end, %object\n"
        ".size g2_at_cmd_table_end, 0\n");
