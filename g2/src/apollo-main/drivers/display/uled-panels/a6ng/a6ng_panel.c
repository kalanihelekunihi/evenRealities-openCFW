/* Hongshi A6N-G micro-LED panel over MSPI0, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\uled\hongshi_a6ng\drv_mspi_a6ng.c.
 * Native 0x5bcc18..0x5bcd29, 0x5bce00..0x5bcf27, 0x5bcf68..0x5bd2b7;
 * literal pool 0x5bd2f0..0x5bd398.
 *
 * Register access (0x5bbdf0 / 0x5bbe3e): a 3-byte serial frame
 * {0x78 (bank 0) | 0x7a (bank 1), reg, value} for writes and instruction
 * 0x79 / 0x7b with the register as address for reads; read_bank retries three
 * times. Health check: an 8-byte raw QSPI frame {02 00 2a 00 00 00 01 df}
 * (DCS 0x2a column window 0..0x1df) must go out, bank-0 register 0xbe must
 * read 0x84 (ASIC), register 0x62 must read 0x77 or 0x57 (panel), and the
 * mirror register sampled by hongshi_read_panel_mirror (bank 0 reg 0xd8 after a
 * 0xd0/0x0b/0x7e/0xd2/0xd4/0x7d test-mode sequence) must have bit 5 set.
 * Recovery = power-off sequence, 1 ms, power-on sequence, re-init. */
#include <stdint.h>
#include <stddef.h>
#include "../uled_mspi_request.h"

extern uint8_t g2_a6ng_status_frame[8]; /* RAM 0x20074130, DMA-able copy of the column-window frame */

extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);              /* 0x439be4 memcpy */
extern uint32_t display_driver_uled_type1_write_register_5bbdf0(uint32_t reg, uint32_t value, uint32_t bank); /* driver_a6ng_write_register */
extern uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t reg, uint32_t bank); /* am_devices_mspi_hongshi_read_bank */
extern uint32_t display_driver_uled_type1_finish_5bcbb4(void); /* hongshi_power_off_sequence */
extern uint32_t display_driver_uled_type1_pre_5bcb6c(void);    /* hongshi_power_on_sequence */
extern uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t power_cycle); /* am_devices_mspi_hongshi_init */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern void g2_norflash_delay_us_491102(uint32_t us);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define A6NG_ASIC_ID_REG   0xbeu
#define A6NG_ASIC_ID       0x84u
#define A6NG_PANEL_ID_REG  0x62u
#define A6NG_PANEL_ID_A    0x77u
#define A6NG_PANEL_ID_B    0x57u
#define A6NG_MIRROR_REG    0xd8u
#define A6NG_MIRROR_OK_BIT 0x20u

static const uint8_t status_frame_rom[8] = { 0x02, 0x00, 0x2a, 0x00, 0x00, 0x00, 0x01, 0xdf }; /* ROM 0x78d484 */
static const g2_uled_mspi_request_t status_write_template = {                                /* ROM 0x76b180 */
    .num_bytes = sizeof status_frame_rom, .buffer = g2_a6ng_status_frame,
};

static const char module_tag[] = "driver.a6n-g"; /* ROM 0x785c80 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c"; /* ROM 0x6ecca8 */
static const char reflash_fn[] = "am_devices_hongshi_QSPI_PartialReflash"; /* ROM 0x74977c */
static const char null_handle[] = "Error - pMspiHandle is NULL\r\n"; /* ROM 0x75f7d0 */
static const char null_handle_short[] = "[driver.a6n-g]Error - pMspiHandle is NULL\r\n"; /* ROM 0x73e424 */
static const char recovery_fn[] = "am_devices_hongshi_status_recovery"; /* ROM 0x753be8 */
static const char recovery_start[] = "hongshi status abnormal, do power recovery\r\n"; /* ROM 0x733644 */
static const char recovery_start_short[] = "[driver.a6n-g]hongshi status abnormal, do power recovery\r\n"; /* ROM 0x714788 */
static const char power_down_done[] = "hongshi power down done"; /* ROM 0x776cf4 */
static const char power_down_done_short[] = "[driver.a6n-g]hongshi power down done"; /* ROM 0x7497a4 */
static const char power_up_done[] = "hongshi power up done"; /* ROM 0x776d0c */
static const char power_up_done_short[] = "[driver.a6n-g]hongshi power up done"; /* ROM 0x753c0c */
static const char init_done[] = "hongshi driver init done"; /* ROM 0x76b110 */
static const char init_done_short[] = "[driver.a6n-g]hongshi driver init done"; /* ROM 0x7497cc */
static const char check_fn[] = "am_devices_hongshi_status_check_and_recovery"; /* ROM 0x733674 */
static const char write_failed[] = "status_check_and_recovery spi write failed, status: 0x%08X\r\n"; /* ROM 0x70afa4 */
static const char write_failed_short[] = "[driver.a6n-g]status_check_and_recovery spi write failed, status: 0x%08X\r\n"; /* ROM 0x6f30f0 */
static const char asic_value[] = "status_check bank0 0xBE = 0x%02X\r\n"; /* ROM 0x753c30 */
static const char asic_value_short[] = "[driver.a6n-g]status_check bank0 0xBE = 0x%02X\r\n"; /* ROM 0x728e70 */
static const char asic_bad[] = "hongshi ASIC abnormal: bank0 0xBE = 0x%02X (expect 0x84), recovery\r\n"; /* ROM 0x6f9efc */
static const char asic_bad_short[] = "[driver.a6n-g]hongshi ASIC abnormal: bank0 0xBE = 0x%02X (expect 0x84), recovery\r\n"; /* ROM 0x6e7684 */
static const char panel_value[] = "status_check bank0 0x62 = 0x%02X\r\n"; /* ROM 0x753c54 */
static const char panel_value_short[] = "[driver.a6n-g]status_check bank0 0x62 = 0x%02X\r\n"; /* ROM 0x728ea4 */
static const char panel_bad[] = "hongshi panel abnormal: bank0 0x62 = 0x%02X (expect 0x77 or 0x57), recovery\r\n"; /* ROM 0x6ecd48 */
static const char panel_bad_short[] = "[driver.a6n-g]hongshi panel abnormal: bank0 0x62 = 0x%02X (expect 0x77 or 0x57), recovery\r\n"; /* ROM 0x6e00c8 */
static const char mirror_value[] = "status_check panel mirror reg = 0x%02X \r\n"; /* ROM 0x73e450 */
static const char mirror_value_short[] = "[driver.a6n-g]status_check panel mirror reg = 0x%02X \r\n"; /* ROM 0x71e258 */
static const char mirror_bad[] = "hongshi panel abnormal: mirror = 0x%02X , recovery\r\n"; /* ROM 0x71e290 */
static const char mirror_bad_short[] = "[driver.a6n-g]hongshi panel abnormal: mirror = 0x%02X , recovery\r\n"; /* ROM 0x7023b0 */
static const char mirror_ok[] = "hongshi panel normal: mirror = 0x%02X\r\n"; /* ROM 0x7497f4 */
static const char mirror_ok_short[] = "[driver.a6n-g]hongshi panel normal: mirror = 0x%02X\r\n"; /* ROM 0x71e2c8 */

static void log0(uint8_t level, const char *fn, uint32_t line, uint32_t compact,
                 const char *text, const char *text_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(compact, text_short, text_short);
}

static void log1(uint8_t level, const char *fn, uint32_t line, uint32_t compact,
                 const char *text, const char *text_short, uint32_t arg)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, text, arg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(compact, text_short, text_short, arg);
}

/* The blocking variant is a stub in this build: it clips and walks the rows
 * and touches the two bytes past each span like the JBD4010 driver, but the
 * QSPI write itself is compiled out. */
uint32_t am_devices_hongshi_QSPI_PartialReflash(int32_t x_off, int32_t y_off, int32_t x0,
                                                int32_t y0, int32_t x1, int32_t y1)
{
    int32_t y;

    if (g2_a6ng_mspi_handle == NULL) {
        log0(1u, reflash_fn, 0x30bu, 0x04000000u, null_handle, null_handle_short);
        return UINT32_MAX;
    }
    if (x1 >= G2_ULED_WIDTH)
        x1 = G2_ULED_WIDTH - 1;
    if (y1 >= G2_ULED_HEIGHT)
        y1 = G2_ULED_HEIGHT - 1;
    for (y = y0; y <= y1; y++) {
        volatile uint8_t *row = g2_a6ng_framebuffer + (y * G2_ULED_WIDTH) / 2 + x0 / 2;
        uint32_t address = (((uint32_t)(y + y_off) << 10) & 0x7fc00u) | ((uint32_t)(x0 + x_off) & 0x3ffu);
        int32_t span = x1 / 2 - x0 / 2;
        uint8_t save0, save1;

        (void)address;
        if (x1 & 1)
            span++;
        save0 = row[span];
        row[span] = 0u;
        save1 = row[span + 1];
        row[span + 1] = 0u;
        row[span] = save0;
        row[span + 1] = save1;
    }
    g2_delay_ms_4910f4(1u);
    return 0u;
}

void am_devices_hongshi_status_recovery(void)
{
    log0(1u, recovery_fn, 0x38bu, 0x04000000u, recovery_start, recovery_start_short);
    (void)display_driver_uled_type1_finish_5bcbb4();
    log0(3u, recovery_fn, 0x38eu, 0x0c000000u, power_down_done, power_down_done_short);
    g2_delay_ms_4910f4(1u);
    (void)display_driver_uled_type1_pre_5bcb6c();
    log0(3u, recovery_fn, 0x392u, 0x0c000000u, power_up_done, power_up_done_short);
    (void)display_driver_uled_option_type1_enable_5bbda4(0u);
    log0(3u, recovery_fn, 0x395u, 0x0c000000u, init_done, init_done_short);
}

/* Enters the bank-0 test window, pulses 0x7d, restores it and returns the
 * mirror status byte (reg 0xd8; 0xff after three failed reads). */
uint32_t hongshi_read_panel_mirror(void)
{
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd0u, 0x05u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x0bu, 0xffu, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x7eu, 0x88u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x7eu, 0x08u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd2u, 0x01u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd4u, 0x18u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x7du, 0x04u, 0u);
    g2_norflash_delay_us_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x7du, 0x00u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd4u, 0x00u, 0u);
    g2_norflash_delay_us_491102(1u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0x0bu, 0x0au, 0u);
    g2_norflash_delay_us_491102(1u);
    return display_driver_uled_type1_read_bank_5bbe80(A6NG_MIRROR_REG, 0u);
}

/* Returns 1 when the panel is healthy, 0 when the probe write failed or a
 * recovery was performed. */
uint32_t am_devices_hongshi_status_check_and_recovery(void)
{
    g2_uled_mspi_request_t request;
    uint32_t status;
    uint8_t value;

    audio_queue_copy_bytes(g2_a6ng_status_frame, status_frame_rom, sizeof status_frame_rom);
    audio_uart_display_area_copy_439c04(&request, &status_write_template, sizeof request);
    request.handle = g2_a6ng_mspi_handle;
    status = display_driver_uled_type0_packet_write_59ccdc(&request);
    if (status != 0u) {
        log1(1u, check_fn, 0x413u, 0x04400000u, write_failed, write_failed_short, status);
        return 0u;
    }

    value = (uint8_t)display_driver_uled_type1_read_bank_5bbe80(A6NG_ASIC_ID_REG, 0u);
    log1(3u, check_fn, 0x41au, 0x0c400000u, asic_value, asic_value_short, value);
    if (value != A6NG_ASIC_ID) {
        log1(1u, check_fn, 0x41cu, 0x04400000u, asic_bad, asic_bad_short, value);
        am_devices_hongshi_status_recovery();
        return 0u;
    }

    value = (uint8_t)display_driver_uled_type1_read_bank_5bbe80(A6NG_PANEL_ID_REG, 0u);
    log1(3u, check_fn, 0x423u, 0x0c400000u, panel_value, panel_value_short, value);
    if (value != A6NG_PANEL_ID_A && value != A6NG_PANEL_ID_B) {
        log1(1u, check_fn, 0x425u, 0x04400000u, panel_bad, panel_bad_short, value);
        am_devices_hongshi_status_recovery();
        return 0u;
    }

    value = (uint8_t)hongshi_read_panel_mirror();
    log1(3u, check_fn, 0x42fu, 0x0c400000u, mirror_value, mirror_value_short, value);
    if ((value & A6NG_MIRROR_OK_BIT) == 0u) {
        log1(1u, check_fn, 0x432u, 0x04400000u, mirror_bad, mirror_bad_short, value);
        am_devices_hongshi_status_recovery();
        return 0u;
    }
    log1(3u, check_fn, 0x436u, 0x0c400000u, mirror_ok, mirror_ok_short, value);
    return 1u;
}
