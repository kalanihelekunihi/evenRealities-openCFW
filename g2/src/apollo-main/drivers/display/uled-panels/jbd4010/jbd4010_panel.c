/* JBD4010 micro-LED panel over MSPI0 (QSPI), stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\uled\jbd4010\drv_mspi_jbd4010.c.
 * Native 0x59271e..0x5927c9, 0x592cb4..0x592de9, 0x59308c..0x5931bf,
 * 0x593334..0x593397 and 0x593750..0x5938c9; literal pools 0x5932f8..0x59333x
 * and 0x5938d4..0x5939a0.
 *
 * Command opcodes (single instruction byte, serial mode): 0xa9 / 0xa3 open and
 * close a register-write window (also around 0xc0 display offset {x, y} in
 * 0x592aa8), 0x46 (6-bit drive current), 0x06 and 0x31 (=4) around it, 0x97
 * (commit/update, sent after every frame and register change), 0x71..0x74
 * (display modes), 0x81 (die-ID read, address phase 0x1fff00 plus turnaround,
 * 12 bytes), 0x9f (chip-ID read, 0x592f9a: id = reply[1] << 8 | reply[2]).
 * Pixel data goes out in quad mode with instruction 0x62 and a 32-bit address
 * word ((row << 10) & 0x7fc00 | column & 0x3ff) << 8 | 0xff, 640x480 at 4 bpp. */
#include <stdint.h>
#include <stddef.h>
#include "../uled_mspi_request.h"

extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);              /* 0x439be4 memcpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                 /* 0x43c0e4 memset */
extern uint32_t display_driver_uled_command_5926ee(uint32_t command, const void *payload, uint32_t length); /* jbd4010_write_command */
extern uint32_t display_driver_uled_type0_frame_lower_592dea(uint32_t, uint32_t, uint32_t, uint32_t,
                                                               uint32_t width, uint32_t height); /* am_devices_jbd4010_QSPI_PartialReflash_async */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern void g2_norflash_delay_us_491102(uint32_t us);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define JBD_CMD_COMMIT     0x97u
#define JBD_CMD_WRITE_DATA 0x62u
#define JBD_CMD_DIE_ID     0x81u
#define JBD_DIE_ID_ADDR    0x1fff00u
#define JBD_DIE_ID_LEN     12u
#define JBD_MODE_A         0x71u
#define JBD_MODE_C         0x73u
#define JBD_MODE_SEQUENCE  0x74u

/* 28-byte request templates in ROM. */
static const g2_uled_mspi_request_t write_template = { .send_instr = 1u };    /* ROM 0x76b260 */
static const g2_uled_mspi_request_t die_read_template = {                    /* ROM 0x76b298 */
    .send_addr = 1u, .send_instr = 1u, .turnaround = 1u,
};

static const char module_tag[] = "driver.jbd4010"; /* ROM 0x785c90 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c"; /* ROM 0x6f313c */
static const char reflash_fn[] = "am_devices_jbd4010_QSPI_PartialReflash"; /* ROM 0x749844 */
static const char reflash_fail[] = "\r\nam_devices_mspi_jbd4010_QSPI_PartialReflash fail\r\n"; /* ROM 0x71e300 */
static const char reflash_fail_short[] = "[driver.jbd4010]\r\nam_devices_mspi_jbd4010_QSPI_PartialReflash fail\r\n"; /* ROM 0x6f9f44 */
static const char die_fn[] = "am_devices_mspi_jbd4010_read_dieId"; /* ROM 0x753cc0 */
static const char die_fail[] = "read die id failed,errno number = %d\r\n"; /* ROM 0x7498bc */
static const char die_fail_short[] = "[driver.jbd4010]read die id failed,errno number = %d\r\n"; /* ROM 0x71e370 */
static const char die_ok[] = "jbd panel die id: %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x"; /* ROM 0x6ecd98 */
static const char die_ok_short[] = "[driver.jbd4010]jbd panel die id: %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x"; /* ROM 0x6dd174 */
static const char mode_fn[] = "am_devices_jbd4010_set_mode"; /* ROM 0x76b20c */
static const char mode_set[] = "jbd4010 set mode = 0x%02x"; /* ROM 0x76b228 */
static const char mode_set_short[] = "[driver.jbd4010]jbd4010 set mode = 0x%02x"; /* ROM 0x73e608 */
static const char mode_fail[] = "jbd4010 set mode failed, mode = 0x%02x"; /* ROM 0x749984 */
static const char mode_fail_short[] = "[driver.jbd4010]jbd4010 set mode failed, mode = 0x%02x"; /* ROM 0x71e3e0 */

/* Quad-mode data write. The first argument is ignored by stock. */
uint32_t jbd4010_write_data_block(uint32_t unused, uint8_t command, uint8_t send_addr,
                                  uint32_t address, void *buffer, uint32_t length)
{
    g2_uled_mspi_request_t request;

    (void)unused;
    audio_uart_display_area_copy_439c04(&request, &write_template, sizeof request);
    request.send_addr = send_addr;
    request.dev_addr = address;
    request.instr = command;
    request.num_bytes = length;
    request.buffer = buffer;
    request.handle = g2_jbd4010_mspi_handle;
    return am_devices_mspi_qspi_write(&request);
}

/* Serial read with address phase and turnaround (die-ID block). */
uint32_t jbd4010_read_die_response(uint8_t command, void *buffer, uint32_t length, uint32_t address)
{
    g2_uled_mspi_request_t request;

    audio_uart_display_area_copy_439c04(&request, &die_read_template, sizeof request);
    request.dev_addr = address;
    request.instr = command;
    request.num_bytes = length;
    request.buffer = buffer;
    request.handle = g2_jbd4010_mspi_handle;
    return display_driver_uled_type0_packet_59cc40(&request);
}

/* Blocking partial refresh of rows y0..y1, columns x0..x1 (clamped to the
 * panel), placed at panel offset (x_off, y_off). Each row is sent from the
 * 4-bpp framebuffer with the two bytes after the span temporarily zeroed. */
uint32_t am_devices_jbd4010_QSPI_PartialReflash(int32_t x_off, int32_t y_off, int32_t x0,
                                                int32_t y0, int32_t x1, int32_t y1)
{
    uint32_t status = 0u;
    uint32_t zero;
    int32_t y;

    if (x1 >= G2_ULED_WIDTH)
        x1 = G2_ULED_WIDTH - 1;
    if (y1 >= G2_ULED_HEIGHT)
        y1 = G2_ULED_HEIGHT - 1;
    for (y = y0; y <= y1; y++) {
        uint8_t *row = g2_jbd4010_framebuffer + (y * G2_ULED_WIDTH) / 2 + x0 / 2;
        uint32_t address = (((uint32_t)(y + y_off) << 10) & 0x7fc00u) | ((uint32_t)(x0 + x_off) & 0x3ffu);
        int32_t span = x1 / 2 - x0 / 2;
        uint8_t save0, save1;

        if (x1 & 1)
            span++;
        save0 = row[span];
        row[span] = 0u;
        save1 = row[span + 1];
        row[span + 1] = 0u;
        status = jbd4010_write_data_block(0u, JBD_CMD_WRITE_DATA, 1u, (address << 8) | 0xffu,
                                          row, (uint32_t)(span + 2));
        row[span] = save0;
        row[span + 1] = save1;
    }
    zero = 0u;
    status |= display_driver_uled_command_5926ee(JBD_CMD_COMMIT, &zero, 0u);
    if (status == 0u) {
        g2_delay_ms_4910f4(1u);
        return 0u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, reflash_fn, 0x1ccu, reflash_fail);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x04000000u, reflash_fail_short, reflash_fail_short);
    g2_delay_ms_4910f4(1u);
    return 1u;
}

/* Reads the 12-byte die ID into out (may be NULL). */
uint32_t am_devices_mspi_jbd4010_read_dieId(uint8_t *out)
{
    uint8_t id[JBD_DIE_ID_LEN];
    uint32_t status;

    audio_uart_buffer_zero(id, sizeof id, 0u);
    status = jbd4010_read_die_response(JBD_CMD_DIE_ID, id, sizeof id, JBD_DIE_ID_ADDR);
    if (status != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, die_fn, 0x268u, die_fail, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08400000u, die_fail_short, die_fail_short, status);
        return UINT32_MAX;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, die_fn, 0x26eu, die_ok,
                           id[0], id[1], id[2], id[3], id[4], id[5],
                           id[6], id[7], id[8], id[9], id[10], id[11]);
    /* Stock builds the compact-log argument field from id[10], not from the
     * argument count. */
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)(id[10] & 0xfu) << 22) | 0x0c000000u,
                                  die_ok_short, die_ok_short,
                                  id[0], id[1], id[2], id[3], id[4], id[5],
                                  id[6], id[7], id[8], id[9], id[10], id[11]);
    if (out != NULL)
        audio_queue_copy_bytes(out, id, sizeof id);
    return 0u;
}

/* Drive current: low six bits of the argument into command 0x46 inside the
 * 0xa9..0xa3 register window, then commit with 0x97. */
uint32_t jbd4010_set_current_6bit(uint8_t current)
{
    uint32_t scratch[5];
    uint32_t value = current & 0x3fu;

    audio_uart_buffer_zero(scratch, sizeof scratch, 0u);
    (void)display_driver_uled_command_5926ee(0x06u, scratch, 0u);
    (void)display_driver_uled_command_5926ee(0xa9u, scratch, 0u);
    (void)display_driver_uled_command_5926ee(0x46u, &value, 1u);
    scratch[0] = 4u;
    (void)display_driver_uled_command_5926ee(0x31u, scratch, 1u);
    (void)display_driver_uled_command_5926ee(0xa3u, scratch, 0u);
    (void)display_driver_uled_command_5926ee(JBD_CMD_COMMIT, scratch, 0u);
    g2_delay_ms_4910f4(1u);
    return 0u;
}

/* Modes 0x71..0x73 are sent directly and followed by a full-frame async
 * reflash; 0x74 sends 0x71 then 0x73 without a reflash. */
uint32_t am_devices_jbd4010_set_mode(uint8_t mode)
{
    uint8_t scratch[20];

    audio_uart_buffer_zero(scratch, sizeof scratch, 0u);
    if (mode == 0x71u || mode == 0x72u || mode == 0x73u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, mode_fn, 0x342u, mode_set, mode);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08400000u, mode_set_short, mode_set_short, mode);
        (void)display_driver_uled_command_5926ee(mode, scratch, 0u);
        g2_norflash_delay_us_491102(2u);
        (void)display_driver_uled_command_5926ee(JBD_CMD_COMMIT, scratch, 0u);
        g2_norflash_delay_us_491102(2000u);
        (void)display_driver_uled_type0_frame_lower_592dea(0u, 0u, 0u, 0u, G2_ULED_WIDTH, G2_ULED_HEIGHT);
        return 0u;
    }
    if (mode == JBD_MODE_SEQUENCE) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, mode_fn, 0x34au, mode_set, mode);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08400000u, mode_set_short, mode_set_short, mode);
        (void)display_driver_uled_command_5926ee(JBD_MODE_A, scratch, 0u);
        g2_norflash_delay_us_491102(2u);
        (void)display_driver_uled_command_5926ee(JBD_MODE_C, scratch, 0u);
        g2_norflash_delay_us_491102(2u);
        (void)display_driver_uled_command_5926ee(JBD_CMD_COMMIT, scratch, 0u);
        g2_norflash_delay_us_491102(2000u);
        return 0u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module_tag, source_file, mode_fn, 0x353u, mode_fail, mode);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x04400000u, mode_fail_short, mode_fail_short, mode);
    return UINT32_MAX;
}
