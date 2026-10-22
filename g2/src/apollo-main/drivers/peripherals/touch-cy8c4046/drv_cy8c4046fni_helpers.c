/* PSoC 4000T touch controller host helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\touch\drv_cy8c4046fni.c.
 * Native 0x55b2ec..0x55b31b, 0x55b340..0x55b3ff, 0x55b5ca..0x55b5e3 and
 * 0x55b64a..0x55b675, 0x55b6a8..0x55b72f; literal pool 0x55b9f0..0x55ba13.
 *
 * These are the transport-table entries and the command wrappers that the
 * rest of drv_cy8c4046fni.c (drv_cy8c4046fni.c in this directory) calls. The
 * command wrappers take the transport table and return -1 when it is NULL,
 * otherwise the I2C HAL status (0 ok, 1 failure). */
#include <stdint.h>
#include <stddef.h>
#include "g2_hal_i2c.h"
#include "g2_touch_cy8c4046.h"

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);     /* 0x43c0e4 memset */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* 0x439be4 memcpy */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value);                /* 0x53a5be */
extern int32_t osDelay(uint32_t ticks);                                          /* 0x449376 */

extern uint8_t g2_touch_version_bytes[4]; /* RAM 0x20074508, last raw version reply */

#define TOUCH_RESET_PIN 10u

/* Stock 0x55b2ec, table entry +0x0: one write of the command byte followed
 * by the body (hal_i2c_transfer_joined). */
uint32_t cy8c4046fni_cmd_write_55b2ec(uint8_t cmd, const void *body, uint16_t len)
{
    uint8_t c = cmd;
    return hal_i2c_transfer_joined(G2_TOUCH_I2C_BUS, G2_TOUCH_I2C_ADDR, &c, 1u, body, len);
}

/* Stock 0x55b304, table entry +0x4: write the command byte, then read the
 * reply in a separate transaction (hal_i2c_transfer_full). */
uint32_t cy8c4046fni_cmd_read_55b304(uint8_t cmd, void *rx, uint16_t len)
{
    uint8_t c = cmd;
    return hal_i2c_transfer_full(G2_TOUCH_I2C_BUS, G2_TOUCH_I2C_ADDR, &c, 1u, rx, len);
}

/* Stock 0x55b340: command 2, enter the touch bootloader. */
int32_t cy8c4046fni_switch_to_dfu_55b340(const g2_touch_ops_t *ops)
{
    if (ops == NULL)
        return -1;
    return (int32_t)ops->cmd_write(G2_TOUCH_CMD_ENTER_DFU, NULL, 0u);
}

/* Stock 0x55b35a: command 3, read the last event report. */
int32_t cy8c4046fni_read_report_55b35a(const g2_touch_ops_t *ops, void *rx, uint8_t len)
{
    if (ops == NULL)
        return -1;
    return (int32_t)ops->cmd_read(G2_TOUCH_CMD_READ_REPORT, rx, len);
}

/* Stock 0x55b374: command 1, read the 4-byte firmware version. */
int32_t cy8c4046fni_cmd_read_version_55b374(const g2_touch_ops_t *ops, void *rx, uint8_t len)
{
    if (ops == NULL)
        return -1;
    return (int32_t)ops->cmd_read(G2_TOUCH_CMD_READ_VERSION, rx, len);
}

/* Stock 0x55b38e: command 5, save the proximity baseline. */
int32_t cy8c4046fni_save_baseline_55b38e(const g2_touch_ops_t *ops)
{
    if (ops == NULL)
        return -1;
    return (int32_t)ops->cmd_write(G2_TOUCH_CMD_SAVE_BASELINE, NULL, 0u);
}

/* Stock 0x55b3a8: command 6, u16 little-endian baseline. */
int32_t cy8c4046fni_read_baseline_55b3a8(const g2_touch_ops_t *ops, uint16_t *baseline)
{
    uint8_t rx[2];
    audio_uart_buffer_zero(rx, sizeof rx, 0u);
    if (ops == NULL || baseline == NULL)
        return -1;
    int32_t ret = (int32_t)ops->cmd_read(G2_TOUCH_CMD_READ_BASELINE, rx, 2u);
    if (ret != 0)
        return ret;
    *baseline = (uint16_t)(rx[0] | (rx[1] << 8));
    return 0;
}

/* Stock 0x55b3ea: a gesture threshold is valid when present and non-zero. */
uint32_t cy8c4046fni_gesture_cfg_valid_55b3ea(const uint16_t *threshold)
{
    if (threshold == NULL)
        return 0u;
    return *threshold != 0u ? 1u : 0u;
}

/* Stock 0x55b5ca: fill a transport table from the ROM entry pointers
 * 0x55b2ed/0x55b305/0x55b31d/0x55b32f. */
void cy8c4046fni_ops_init_55b5ca(g2_touch_ops_t *ops)
{
    ops->cmd_write = cy8c4046fni_cmd_write_55b2ec;
    ops->cmd_read = cy8c4046fni_cmd_read_55b304;
    ops->write = cy8c4046fni_i2c_write_55b31c;
    ops->read = cy8c4046fni_i2c_read_55b32e;
}

/* Stock 0x55b64a: pulse the touch reset line (pin 10 low 10 ticks, high,
 * then 50 ticks settle). */
void cy8c4046fni_reset_55b64a(void)
{
    (void)g2_codec_pin_write(TOUCH_RESET_PIN, 0u);
    (void)osDelay(10u);
    (void)g2_codec_pin_write(TOUCH_RESET_PIN, 1u);
    (void)osDelay(50u);
}

/* Stock 0x55b66a: install the transport table at RAM 0x20073e24. */
void DRV_TouchInit_55b66a(void)
{
    cy8c4046fni_ops_init_55b5ca(&g2_touch_ops);
}

/* Stock 0x55b6a8: command 4, copy the 10-byte sensor diff block to out on
 * success. Always returns 0. */
int32_t DRV_TouchReadSensorDiff_55b6a8(void *out)
{
    uint8_t rx[10];
    audio_uart_buffer_zero(rx, sizeof rx, 0u);
    if (g2_touch_ops.cmd_read(G2_TOUCH_CMD_READ_SENSOR_DIFF, rx, sizeof rx) != 0u)
        return 0;
    (void)audio_queue_copy_bytes(out, rx, sizeof rx);
    return 0;
}

/* Stock 0x55b6dc: command 1. The raw reply is kept at RAM 0x20074508 and
 * returned big-endian, whatever the transport status. */
int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version)
{
    uint8_t rx[4];
    audio_uart_buffer_zero(rx, sizeof rx, 0u);
    if (version == NULL)
        return -1;
    int32_t ret = cy8c4046fni_cmd_read_version_55b374(&g2_touch_ops, rx, 4u);
    g2_touch_version_bytes[0] = rx[0];
    g2_touch_version_bytes[1] = rx[1];
    g2_touch_version_bytes[2] = rx[2];
    g2_touch_version_bytes[3] = rx[3];
    *version = ((uint32_t)g2_touch_version_bytes[0] << 24) |
               ((uint32_t)g2_touch_version_bytes[1] << 16) |
               ((uint32_t)g2_touch_version_bytes[2] << 8) |
               (uint32_t)g2_touch_version_bytes[3];
    return ret;
}
