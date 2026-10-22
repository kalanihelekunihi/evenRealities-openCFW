/* Macronix MX25U25643G NOR driver (MSPI1), stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c.
 * Object 0x46f4a4..0x471163. This unit holds the init, reset, ID, MSPI timing
 * scan, 4-byte-address and quad-enable bodies: 0x46f546..0x46f5a5,
 * 0x46f788..0x46fb0b, 0x46fe38..0x470155, 0x4703c6..0x470665,
 * 0x470aac..0x470d59. The other bodies of the same object are anchored in
 * drivers/flash/{fal-norflash,nor,norflash}, ui/freetype/font-flash and
 * app/brightness-prepare.
 *
 * Opcodes used here: RDID 0x9f (3 bytes, ID 0x2539c2 as packed by the read
 * helper), RSTEN 0x66 / RST 0x99, RDCR 0x15 (bit 5 = 4BYTE), EN4B 0xb7,
 * RDSR 0x05 (bit 6 = QE, bits 2..5 = BP0..BP3), WRSR 0x01. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* am_hal_mspi timing record handed to the 0x4c0f78 selector 16 request. */
typedef struct {
    uint8_t tx_neg;        /* +0 */
    uint8_t rx_neg;        /* +1 */
    uint8_t rx_cap;        /* +2 */
    uint8_t tx_dqs_delay;  /* +3 */
    uint8_t rx_dqs_delay;  /* +4 */
    uint8_t turnaround;    /* +5 */
} g2_mspi_timing_t;
_Static_assert(sizeof(g2_mspi_timing_t) == 6, "MSPI timing record is 6 bytes");

/* CMSIS-RTOS2 osMutexAttr_t. */
typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
} g2_os_mutex_attr_t;

#define TIMING_SETTINGS 36u
#define RX_DQS_STEPS 32u
#define MX25U25643G_ID 0x2539c2u
#define MSPI_SET_TIMING 16u
#define MSPI_MODULE 1u

extern volatile uint32_t g2_norflash_controller_handle_20074544; /* RAM 0x20074544 */
extern void *audio_uart_font_flash_mutex;                       /* RAM 0x20074548 */
extern void *g2_norflash_device_context_20074540;              /* RAM 0x20074540 */
extern g2_mspi_timing_t g2_mspi_timing_config_20000820;        /* RAM 0x20000820 (8-byte slot) */
extern const g2_mspi_timing_t g2_mspi_timing_table_20000828[TIMING_SETTINGS]; /* RAM 0x20000828 */
extern uint8_t g2_flash_mutex_cb[0x50];                         /* RAM 0x20072a88 */

extern void *osMutexNew(const void *attr);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *memset_43bb00(void *dst, int32_t value, uint32_t length);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* memcpy 0x439be4 */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t controller, uint32_t request,
                                                   const void *payload);
extern uint32_t mx25u25643g_mspi_init_46fb0c(uint32_t module, uint32_t mode, void **context);
extern uint32_t timing_window_length_46f6e6(const uint32_t *mask);
extern uint32_t timing_window_center_46f6fa(const uint32_t *mask);
extern void audio_uart_brightness_close_prepare_46f50c(void);
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void g2_norflash_enter_470f68(void);
extern void g2_norflash_exit_470e90(void);
extern uint32_t g2_norflash_command_470168(uint32_t command, uint32_t address, uint32_t mode,
                                           uint8_t *response, uint32_t count);
extern uint32_t g2_norflash_erase_command_47021c(uint32_t command, uint32_t address, uint32_t mode,
                                                 uint32_t data_pointer, uint32_t count);
extern uint32_t g2_norflash_wait_idle_4703ba(void);
extern uint32_t g2_norflash_write_enable_470670(void);
extern uint32_t g2_norflash_write_disable_4706e0(void);

uint32_t DRV_Mx25u25643g_read_id_470028(uint32_t *id);
void DRV_Mx25u25643g_SoftReset_46ff5c(void);
uint32_t mx25u25643g_enter_4byte_mode_4704ac(void);
uint32_t mx25u25643g_is_4byte_mode_4703c6(void);
uint32_t mx25u25643g_quad_enable_470aac(uint8_t enable);
void mspi_timing_auto_check_46f9f6(void);
void mspi_flash_mutex_init_46f546(void);

static const char module_tag[] = "drv.norflash"; /* ROM 0x785cd0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c"; /* ROM 0x70258c */
static const char mutex_name[] = "flash_mutex"; /* ROM 0x78a8f8 */
static const char mutex_init_fn[] = "mspi_flash_mutex_init"; /* ROM 0x776e8c */
static const char timing_check_fn[] = "mspi_timing_check"; /* ROM 0x77f0b8 */
static const char timing_auto_fn[] = "mspi_timing_auto_check"; /* ROM 0x776ed4 */
static const char init_fn[] = "DRV_Mx25u25643g_init"; /* ROM 0x776eec */
static const char reset_fn[] = "DRV_Mx25u25643g_SoftReset"; /* ROM 0x76b35c */
static const char read_id_fn[] = "DRV_Mx25u25643g_read_id"; /* ROM 0x776f1c */
static const char device_id_fn[] = "mx25u25643g_get_device_id"; /* ROM 0x76b394 */
static const char is_4byte_fn[] = "mx25u25643g_is_4byte_mode"; /* ROM 0x76b3cc */
static const char enter_4byte_fn[] = "mx25u25643g_enter_4byte_mode"; /* ROM 0x75f990 */
static const char quad_fn[] = "mx25u25643g_quad_enable"; /* ROM 0x776f7c */

static const char mutex_fail[] = "failed to Create mspi_flash_mutex_id"; /* ROM 0x749a4c */
static const char mutex_fail_short[] = "[drv.norflash]failed to Create mspi_flash_mutex_id"; /* ROM 0x7290e0 */
static const char window_fmt[] = "Timing Scan found a window %d fine steps wide in setting %d."; /* ROM 0x70b164 */
static const char window_short[] =
    "[drv.norflash]Timing Scan found a window %d fine steps wide in setting %d."; /* ROM 0x6f3188 */
static const char setting_fmt[] = "TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, Turnaround %d == 0x%08X"; /* ROM 0x6fa01c */
static const char setting_short[] =
    "[drv.norflash]TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, Turnaround %d == 0x%08X"; /* ROM 0x6e76d8 */
static const char rxdqs_fmt[] = "RxDQSDelay is set to %d."; /* ROM 0x76b340 */
static const char rxdqs_short[] = "[drv.norflash]RxDQSDelay is set to %d."; /* ROM 0x749a9c */
static const char scan_ok[] =
    "Time scan success, use scan timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d"; /* ROM 0x6380bc */
static const char scan_ok_short[] =
    "[drv.norflash]Time scan success, use scan timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d"; /* ROM 0x6d46e0 */
static const char scan_fail[] =
    "Time scan failed, use default timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d"; /* ROM 0x64aa14 */
static const char scan_fail_short[] =
    "[drv.norflash]Time scan failed, use default timing parameters: TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, RxDQSDelay %d, Turnaround %d"; /* ROM 0x6d416c */
static const char init_fail[] = "Flash init fail: %d\n"; /* ROM 0x776f04 */
static const char init_fail_short[] = "[drv.norflash]Flash init fail: %d\n"; /* ROM 0x753e94 */
static const char id_fail[] = "Flash ID fail: %d\n"; /* ROM 0x77f0cc */
static const char id_fail_short[] = "[drv.norflash]Flash ID fail: %d\n"; /* ROM 0x753eb8 */
static const char id_fmt[] = "Flash ID: 0x%06X\n"; /* ROM 0x77f0e0 */
static const char id_short[] = "[drv.norflash]Flash ID: 0x%06X\n"; /* ROM 0x75f970 */
static const char rsten_fail[] = "mx25u25643g RSTEN error\n"; /* ROM 0x76b378 */
static const char rsten_fail_short[] = "[drv.norflash]mx25u25643g RSTEN error\n"; /* ROM 0x749b14 */
/* Stock reuses the sector-erase message for a failed RST (0x99). */
static const char rst_fail[] = "Write enable failed before sector erase\n"; /* ROM 0x73e710 */
static const char rst_fail_short[] = "[drv.norflash]Write enable failed before sector erase\n"; /* ROM 0x71e6b8 */
static const char read_fail[] = "command_read ERROR\n"; /* ROM 0x77f0f4 */
static const char read_fail_short[] = "[drv.norflash]command_read ERROR\n"; /* ROM 0x753edc */
static const char device_id_fail[] = "mx25u25643g_get_device_id: init fail=%d"; /* ROM 0x749b3c */
static const char device_id_fail_short[] = "[drv.norflash]mx25u25643g_get_device_id: init fail=%d"; /* ROM 0x71e6f0 */
static const char addr3_fmt[] = "43G is 3byte device address mode\n"; /* ROM 0x753f00 */
static const char addr3_short[] = "[drv.norflash]43G is 3byte device address mode\n"; /* ROM 0x7338e4 */
static const char read4_fail[] = "Read 4byte mode failed\n"; /* ROM 0x776f34 */
static const char read4_fail_short[] = "[drv.norflash]Read 4byte mode failed\n"; /* ROM 0x749b8c */
static const char busy_fmt[] = "Device is busy\n"; /* ROM 0x785ce0 */
static const char busy_short[] = "[drv.norflash]Device is busy\n"; /* ROM 0x75f9b0 */
static const char wren4_fail[] = "Write enable failed before entering 4-byte mode\n"; /* ROM 0x7291e4 */
static const char wren4_fail_short[] = "[drv.norflash]Write enable failed before entering 4-byte mode\n"; /* ROM 0x70b1a4 */
static const char en4b_fail[] = "Failed to enter 4-byte mode\n"; /* ROM 0x75f9d0 */
static const char en4b_fail_short[] = "[drv.norflash]Failed to enter 4-byte mode\n"; /* ROM 0x73e73c */
static const char verify4_fail[] = "Failed to verify 4-byte mode\n"; /* ROM 0x75f9f0 */
static const char verify4_fail_short[] = "[drv.norflash]Failed to verify 4-byte mode\n"; /* ROM 0x73e768 */
static const char wrdi_fail[] = "exit write enable fail\n"; /* ROM 0x776f4c */
static const char wrdi_fail_short[] = "[drv.norflash]exit write enable fail\n"; /* ROM 0x749bb4 */
static const char rdsr_fail[] = "Failed to read status register 2\n"; /* ROM 0x753f6c */
static const char rdsr_fail_short[] = "[drv.norflash]Failed to read status register 2\n"; /* ROM 0x733a04 */
static const char qe_same[] = "QE bit already in desired state\n"; /* ROM 0x753f90 */
static const char qe_same_short[] = "[drv.norflash]QE bit already in desired state\n"; /* ROM 0x733a34 */
static const char wren_qe_fail[] = "Write enable failed before setting QE\n"; /* ROM 0x749bdc */
static const char wren_qe_fail_short[] = "[drv.norflash]Write enable failed before setting QE\n"; /* ROM 0x71e7d0 */
static const char wrsr_fail[] = "Failed to write status register 2\n"; /* ROM 0x753fb4 */
static const char wrsr_fail_short[] = "[drv.norflash]Failed to write status register 2\n"; /* ROM 0x729280 */
static const char qe_verify_fail[] = "Failed to verify QE bit\n"; /* ROM 0x76b404 */
static const char qe_verify_fail_short[] = "[drv.norflash]Failed to verify QE bit\n"; /* ROM 0x749c04 */
static const char qe_fail_fmt[] = "Failed to %s QE bit\n"; /* ROM 0x776f94 */
static const char qe_fail_short[] = "[drv.norflash]Failed to %s QE bit\n"; /* ROM 0x753fd8 */
static const char word_set[] = "set"; /* ROM 0x470f58 */
static const char word_clear[] = "clear"; /* ROM 0x78d48c */

/* ROM 0x785cf0: static control block 0x50 bytes at RAM 0x20072a88. */
static const g2_os_mutex_attr_t flash_mutex_attr = {
    mutex_name, 0u, g2_flash_mutex_cb, sizeof g2_flash_mutex_cb,
};

#define LOG(level, function, line, token, format, short_format, ...)                     \
    do {                                                                                 \
        if ((audio_log_flags() & 2u) != 0u)                                              \
            audio_log_extended((level), module_tag, source_file, (function), (line),    \
                               (format), ##__VA_ARGS__);                                \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)           \
            (void)compress_log_output((token), (short_format), (short_format),          \
                                      ##__VA_ARGS__);                                   \
    } while (0)

void mspi_flash_mutex_init_46f546(void)
{
    if (audio_uart_font_flash_mutex != NULL)
        return;
    audio_uart_font_flash_mutex = osMutexNew(&flash_mutex_attr);
    if (audio_uart_font_flash_mutex == NULL)
        LOG(1u, mutex_init_fn, 0xbau, 0x04000000u, mutex_fail, mutex_fail_short);
}

/* For each of the 36 base settings, sweeps RxDQSDelay 0..31 with turnaround 8
 * and records which steps read the expected JEDEC ID; the setting with the
 * longest passing run wins and RxDQSDelay is placed in that run. */
uint32_t mspi_timing_check_46f788(g2_mspi_timing_t *result)
{
    uint32_t id = 0u;
    uint32_t pass[TIMING_SETTINGS];
    g2_mspi_timing_t probe;

    (void)memset_43bb00(pass, 0, sizeof pass);
    (void)memset_43bb00(&probe, 0, sizeof probe);
    for (uint32_t setting = 0; setting < TIMING_SETTINGS; setting++) {
        probe.tx_neg = g2_mspi_timing_table_20000828[setting].tx_neg;
        probe.rx_neg = g2_mspi_timing_table_20000828[setting].rx_neg;
        probe.rx_cap = g2_mspi_timing_table_20000828[setting].rx_cap;
        probe.tx_dqs_delay = g2_mspi_timing_table_20000828[setting].tx_dqs_delay;
        probe.turnaround = 8u;
        for (uint8_t step = 0; step < RX_DQS_STEPS; step++) {
            probe.rx_dqs_delay = step;
            (void)g2_norflash_config_transfer_4c0f78(g2_norflash_controller_handle_20074544,
                                                     MSPI_SET_TIMING, &probe);
            if (DRV_Mx25u25643g_read_id_470028(&id) == 0u && id == MX25U25643G_ID)
                pass[setting] |= 1u << step;
        }
    }
    uint32_t best = 0u;
    uint32_t widest = 0u;
    for (uint32_t setting = 0; setting < TIMING_SETTINGS; setting++) {
        uint32_t width = timing_window_length_46f6e6(&pass[setting]);
        if (widest < width) {
            best = setting;
            widest = width;
        }
    }
    const g2_mspi_timing_t *row = &g2_mspi_timing_table_20000828[best];
    LOG(2u, timing_check_fn, 0x1c6u, 0x08800000u, window_fmt, window_short, widest, best);
    LOG(2u, timing_check_fn, 0x1cdu, 0x09800000u, setting_fmt, setting_short,
        (uint32_t)row->tx_neg, (uint32_t)row->rx_neg, (uint32_t)row->rx_cap,
        (uint32_t)row->tx_dqs_delay, (uint32_t)row->turnaround, pass[best]);
    uint32_t rx_dqs = timing_window_center_46f6fa(&pass[best]);
    LOG(2u, timing_check_fn, 0x1d3u, 0x08400000u, rxdqs_fmt, rxdqs_short, rx_dqs);
    result->rx_dqs_delay = (uint8_t)rx_dqs;
    result->tx_neg = row->tx_neg;
    result->rx_neg = row->rx_neg;
    result->rx_cap = row->rx_cap;
    result->tx_dqs_delay = row->tx_dqs_delay;
    result->turnaround = row->turnaround;
    return 0u;
}

/* On success the 8-byte slot at 0x20000820 takes the scan result (the stock
 * copies two words from a 6-byte-cleared local). */
void mspi_timing_auto_check_46f9f6(void)
{
    uint32_t scan[2];
    g2_mspi_timing_t *config = &g2_mspi_timing_config_20000820;
    (void)memset_43bb00(scan, 0, 6u);
    if (mspi_timing_check_46f788((g2_mspi_timing_t *)(void *)scan) == 0u) {
        audio_uart_checksum_copy(config, scan, 8u);
        LOG(2u, timing_auto_fn, 499u, 0x09800000u, scan_ok, scan_ok_short,
            (uint32_t)config->tx_neg, (uint32_t)config->rx_neg, (uint32_t)config->rx_cap,
            (uint32_t)config->tx_dqs_delay, (uint32_t)config->rx_dqs_delay,
            (uint32_t)config->turnaround);
    } else {
        LOG(1u, timing_auto_fn, 0x1fbu, 0x05800000u, scan_fail, scan_fail_short,
            (uint32_t)config->tx_neg, (uint32_t)config->rx_neg, (uint32_t)config->rx_cap,
            (uint32_t)config->tx_dqs_delay, (uint32_t)config->rx_dqs_delay,
            (uint32_t)config->turnaround);
    }
}

/* MSPI1 bring-up: reset, serial mode, timing scan, ID check, EN4B, QE=1,
 * mutex; the device is always put back to deep sleep. */
uint32_t DRV_Mx25u25643g_init_46fe38(void)
{
    uint32_t id;
    uint32_t result = mx25u25643g_mspi_init_46fb0c(MSPI_MODULE, 0u, &g2_norflash_device_context_20074540);
    if (result != 0u) {
        LOG(1u, init_fn, 0x284u, 0x04400000u, init_fail, init_fail_short, result);
    } else {
        g2_delay_ms_4910f4(10u);
        DRV_Mx25u25643g_SoftReset_46ff5c();
        g2_norflash_enter_470f68();
        mspi_timing_auto_check_46f9f6();
        g2_norflash_enter_470f68();
        result = DRV_Mx25u25643g_read_id_470028(&id);
        if (result != 0u) {
            LOG(1u, init_fn, 0x28eu, 0x04400000u, id_fail, id_fail_short, result);
        } else {
            LOG(3u, init_fn, 0x292u, 0x0c400000u, id_fmt, id_short, id);
            (void)mx25u25643g_enter_4byte_mode_4704ac();
            (void)mx25u25643g_quad_enable_470aac(1u);
            mspi_flash_mutex_init_46f546();
        }
    }
    audio_uart_brightness_close_prepare_46f50c();
    return result;
}

void DRV_Mx25u25643g_SoftReset_46ff5c(void)
{
    if (g2_norflash_erase_command_47021c(0x66u, 0u, 0u, 0u, 0u) != 0u)
        LOG(1u, reset_fn, 0x2c4u, 0x04000000u, rsten_fail, rsten_fail_short);
    g2_delay_ms_4910f4(1u);
    if (g2_norflash_erase_command_47021c(0x99u, 0u, 0u, 0u, 0u) != 0u)
        LOG(1u, reset_fn, 0x2c9u, 0x04000000u, rst_fail, rst_fail_short);
    g2_delay_ms_4910f4(50u);
}

/* RDID: returns the three response bytes packed as b0 << 16 | b1 << 8 | b2. */
uint32_t DRV_Mx25u25643g_read_id_470028(uint32_t *id)
{
    uint8_t response[4];
    uint32_t result = g2_norflash_command_470168(0x9fu, 0u, 0u, response, 3u);
    if (result != 0u) {
        LOG(1u, read_id_fn, 0x2d8u, 0x04000000u, read_fail, read_fail_short);
        return result;
    }
    *id = (uint32_t)response[1] << 8 | (uint32_t)response[0] << 16 | (uint32_t)response[2];
    return result;
}

/* Returns 0 with the 24-bit ID, -1 for a NULL output, -3 when the lazy init
 * fails and -2 when RDID fails. */
int32_t mx25u25643g_get_device_id_4700b4(uint32_t *id)
{
    uint32_t value;
    if (id == NULL)
        return -1;
    if (g2_norflash_controller_handle_20074544 == 0u) {
        uint32_t result = DRV_Mx25u25643g_init_46fe38();
        if (result != 0u) {
            LOG(1u, device_id_fn, 0x2edu, 0x04400000u, device_id_fail, device_id_fail_short, result);
            return -3;
        }
    }
    g2_norflash_lock_46f65e();
    g2_norflash_enter_470f68();
    value = 0u;
    uint32_t result = DRV_Mx25u25643g_read_id_470028(&value);
    g2_norflash_exit_470e90();
    g2_norflash_unlock_46f674();
    if (result != 0u)
        return -2;
    *id = value & 0xffffffu;
    return 0;
}

/* RDCR bit 5: 1 when the device is in 4-byte address mode, 0 when not, or the
 * transfer status on failure. */
uint32_t mx25u25643g_is_4byte_mode_4703c6(void)
{
    uint8_t config[5];
    (void)memset_43bb00(config, 0, sizeof config);
    uint32_t result = g2_norflash_command_470168(0x15u, 0u, 0u, config, 1u);
    if (result != 0u) {
        LOG(2u, is_4byte_fn, 0x3b0u, 0x08000000u, read4_fail, read4_fail_short);
        return result;
    }
    if ((config[0] & 0x20u) != 0u)
        return 1u;
    LOG(2u, is_4byte_fn, 0x3b8u, 0x08000000u, addr3_fmt, addr3_short);
    return 0u;
}

/* Returns 2 without a controller, 3 when busy, 1 when EN4B does not stick,
 * otherwise the first failing transfer status (0 on success). */
uint32_t mx25u25643g_enter_4byte_mode_4704ac(void)
{
    uint32_t result;
    if (g2_norflash_controller_handle_20074544 == 0u)
        return 2u;
    if (g2_norflash_wait_idle_4703ba() != 0u) {
        LOG(2u, enter_4byte_fn, 0x3c8u, 0x08000000u, busy_fmt, busy_short);
        return 3u;
    }
    result = g2_norflash_write_enable_470670();
    if (result != 0u) {
        LOG(2u, enter_4byte_fn, 0x3cfu, 0x08000000u, wren4_fail, wren4_fail_short);
        return result;
    }
    result = g2_norflash_erase_command_47021c(0xb7u, 0u, 0u, 0u, 0u);
    if (result != 0u) {
        LOG(2u, enter_4byte_fn, 0x3d6u, 0x08000000u, en4b_fail, en4b_fail_short);
        return result;
    }
    (void)g2_norflash_wait_idle_4703ba();
    if (mx25u25643g_is_4byte_mode_4703c6() == 0u) {
        LOG(2u, enter_4byte_fn, 0x3deu, 0x08000000u, verify4_fail, verify4_fail_short);
        return 1u;
    }
    result = g2_norflash_write_disable_4706e0();
    if (result != 0u) {
        LOG(2u, enter_4byte_fn, 0x3e4u, 0x08000000u, wrdi_fail, wrdi_fail_short);
        return result;
    }
    return 0u;
}

/* Sets or clears status-register QE (bit 6) and clears BP0..BP3. Returns 2
 * without a controller, 1 when the readback disagrees, else the status. */
uint32_t mx25u25643g_quad_enable_470aac(uint8_t enable)
{
    uint8_t status[4];
    uint32_t result;
    if (g2_norflash_controller_handle_20074544 == 0u)
        return 2u;
    (void)g2_norflash_wait_idle_4703ba();
    result = g2_norflash_command_470168(0x05u, 0u, 0u, status, 1u);
    if (result != 0u) {
        LOG(2u, quad_fn, 0x521u, 0x08000000u, rdsr_fail, rdsr_fail_short);
        return result;
    }
    if (((status[0] >> 6) & 1u) == enable && (status[0] & 0x3cu) == 0u) {
        LOG(2u, quad_fn, 0x52au, 0x08000000u, qe_same, qe_same_short);
        return 0u;
    }
    result = g2_norflash_write_enable_470670();
    if (result != 0u) {
        LOG(2u, quad_fn, 0x531u, 0x08000000u, wren_qe_fail, wren_qe_fail_short);
        return result;
    }
    if (enable == 0u)
        status[0] &= 0xbfu;
    else
        status[0] |= 0x40u;
    status[0] &= 0xc3u;
    result = g2_norflash_erase_command_47021c(0x01u, 0u, 0u, (uint32_t)(uintptr_t)status, 1u);
    if (result != 0u) {
        LOG(2u, quad_fn, 0x540u, 0x08000000u, wrsr_fail, wrsr_fail_short);
        return result;
    }
    (void)g2_norflash_wait_idle_4703ba();
    result = g2_norflash_command_470168(0x05u, 0u, 0u, status, 1u);
    if (result != 0u) {
        LOG(2u, quad_fn, 0x54au, 0x08000000u, qe_verify_fail, qe_verify_fail_short);
        return result;
    }
    if (((status[0] >> 6) & 1u) == enable)
        return 0u;
    LOG(2u, quad_fn, 0x550u, 0x08400000u, qe_fail_fmt, qe_fail_short,
        enable != 0u ? word_set : word_clear);
    return 1u;
}
