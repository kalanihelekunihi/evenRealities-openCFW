/* PSoC 4000T touch controller host driver, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\touch\drv_cy8c4046fni.c.
 * Module native 0x55b2ec..0x55b9c5, literal pool 0x55b9c8..0x55ba63.
 *
 * This unit holds the stock functions at 0x55b31c, 0x55b32e, 0x55b400,
 * 0x55b530, 0x55b5e4, 0x55b676, 0x55b730, 0x55b78a, 0x55b840 and 0x55b92a.
 * The remaining helpers of the same stock file (0x55b2ec, 0x55b304,
 * 0x55b340..0x55b3ea, 0x55b5ca, 0x55b64a, 0x55b66a, 0x55b6a8, 0x55b6dc) are
 * reconstructed in another unit and are only declared here.
 *
 * Bus 5, address 0x0c; command IDs and the ACK format are documented in
 * g2_touch_cy8c4046.h. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_hal_i2c.h"
#include "g2_touch_cy8c4046.h"

#define GESTURE_ACK_ID   0x07u /* echo of G2_TOUCH_CMD_WRITE_GESTURE_CFG */
#define GESTURE_ACK_END  0x17u

/* Same-file helpers (stock 0x55b340..0x55b3ea): each returns -1 for a NULL
 * table, otherwise the transport status. */
extern int32_t cy8c4046fni_switch_to_dfu_55b340(const g2_touch_ops_t *ops);            /* cmd 2 */
extern int32_t cy8c4046fni_read_report_55b35a(const g2_touch_ops_t *ops, void *rx, uint8_t len); /* cmd 3 */
extern int32_t cy8c4046fni_save_baseline_55b38e(const g2_touch_ops_t *ops);            /* cmd 5 */
extern int32_t cy8c4046fni_read_baseline_55b3a8(const g2_touch_ops_t *ops, uint16_t *baseline); /* cmd 6 */
extern uint32_t cy8c4046fni_gesture_cfg_valid_55b3ea(const uint16_t *threshold);       /* non-NULL and non-zero */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);      /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* 0x439be4 memcpy */

static const char module_tag[] = "drv.touch"; /* ROM 0x78a8e0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\touch\\drv_cy8c4046fni.c"; /* ROM 0x702328 */
static const char fn_write_gesture_cfg[] = "_cy8c4046fniWriteGestureCfg"; /* ROM 0x76b04c */
static const char fn_read_gesture_cfg[] = "_cy8c4046fniReadGestureCfg"; /* ROM 0x76b068 */
static const char fn_switch2dfu[] = "DRV_TouchSwitch2Dfu"; /* ROM 0x77efa0 */
static const char fn_save_baseline[] = "DRV_TouchSaveProximityBaseline"; /* ROM 0x75f710 */
static const char fn_read_baseline[] = "DRV_TouchReadProximityBaseline"; /* ROM 0x75f730 */
static const char fn_drv_write_gesture_cfg[] = "DRV_TouchWriteGestureCfg"; /* ROM 0x76b084 */
static const char fn_drv_read_gesture_cfg[] = "DRV_TouchReadGestureCfg"; /* ROM 0x776c1c */

static const char ack_invalid[] = "gesture cfg ack invalid: %02X %02X %02X"; /* ROM 0x74959c */
static const char ack_invalid_short[] = "[drv.touch]gesture cfg ack invalid: %02X %02X %02X"; /* ROM 0x728c9c */
static const char write_rejected[] = "gesture cfg write rejected, status: %02X"; /* ROM 0x73e240 */
static const char write_rejected_short[] = "[drv.touch]gesture cfg write rejected, status: %02X"; /* ROM 0x728cd0 */
static const char cfg_invalid[] = "gesture cfg invalid: threshold=%u"; /* ROM 0x753a5c */
static const char cfg_invalid_short[] = "[drv.touch]gesture cfg invalid: threshold=%u"; /* ROM 0x733524 */
static const char switch2dfu_failed[] = "DRV_TouchSwitch2Dfu failed: %02X"; /* ROM 0x753a80 */
static const char switch2dfu_failed_short[] = "[drv.touch]DRV_TouchSwitch2Dfu failed: %02X"; /* ROM 0x73e26c */
static const char save_baseline_failed[] = "DRV_TouchSaveProximityBaseline failed: %02X"; /* ROM 0x73e298 */
static const char save_baseline_failed_short[] = "[drv.touch]DRV_TouchSaveProximityBaseline failed: %02X"; /* ROM 0x71e178 */
static const char read_baseline_failed[] = "DRV_TouchReadProximityBaseline failed: %02X"; /* ROM 0x73e2c4 */
static const char read_baseline_failed_short[] = "[drv.touch]DRV_TouchReadProximityBaseline failed: %02X"; /* ROM 0x71e1b0 */
static const char read_baseline_ok[] = "DRV_TouchReadProximityBaseline success: %u (0x%04X)"; /* ROM 0x728d04 */
static const char read_baseline_ok_short[] = "[drv.touch]DRV_TouchReadProximityBaseline success: %u (0x%04X)"; /* ROM 0x70ae64 */
static const char write_cfg_failed[] = "DRV_TouchWriteGestureCfg failed: threshold=%u ret=%d"; /* ROM 0x71e1e8 */
static const char write_cfg_failed_short[] = "[drv.touch]DRV_TouchWriteGestureCfg failed: threshold=%u ret=%d"; /* ROM 0x70aea4 */
static const char write_cfg_null[] = "DRV_TouchWriteGestureCfg failed: cfg is NULL ret=%d"; /* ROM 0x728d38 */
static const char write_cfg_null_short[] = "[drv.touch]DRV_TouchWriteGestureCfg failed: cfg is NULL ret=%d"; /* ROM 0x70aee4 */
static const char write_cfg_ok[] = "DRV_TouchWriteGestureCfg success: threshold=%u"; /* ROM 0x733554 */
static const char write_cfg_ok_short[] = "[drv.touch]DRV_TouchWriteGestureCfg success: threshold=%u"; /* ROM 0x7145e4 */
static const char read_cfg_failed[] = "DRV_TouchReadGestureCfg failed: ret=%d"; /* ROM 0x7495c4 */
static const char read_cfg_failed_short[] = "[drv.touch]DRV_TouchReadGestureCfg failed: ret=%d"; /* ROM 0x728d6c */
static const char read_cfg_ok[] = "DRV_TouchReadGestureCfg success: threshold=%u"; /* ROM 0x733584 */
static const char read_cfg_ok_short[] = "[drv.touch]DRV_TouchReadGestureCfg success: threshold=%u"; /* ROM 0x714620 */

/* Stock logging pattern: extended record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. The compressed mask is
 * (level << 26) | (argument count << 22). */
#define LOG_MASK(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define TOUCH_LOG(level, nargs, line, fn, msg, msg_short, ...)                          \
    do {                                                                                \
        if (audio_log_flags() & 2u)                                                     \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg),   \
                               ##__VA_ARGS__);                                          \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                       \
            (void)compress_log_output(LOG_MASK(level, nargs), (msg_short), (msg_short), \
                                      ##__VA_ARGS__);                                   \
    } while (0)

/* Stock 0x55b31c: transport entry +0x8. */
uint32_t cy8c4046fni_i2c_write_55b31c(const void *tx, uint16_t len)
{
    return hal_i2c_transfer_write(G2_TOUCH_I2C_BUS, G2_TOUCH_I2C_ADDR, tx, len);
}

/* Stock 0x55b32e: transport entry +0xc. */
uint32_t cy8c4046fni_i2c_read_55b32e(void *rx, uint16_t len)
{
    return hal_i2c_transfer_read(G2_TOUCH_I2C_BUS, G2_TOUCH_I2C_ADDR, rx, len);
}

/* Stock 0x55b400 (_cy8c4046fniWriteGestureCfg): command 7 with the u16 LE
 * threshold, then a raw 3-byte ACK read that must be 07 00 17. Returns -1
 * for a NULL table, the transport status on bus failure, 0xff for a zero
 * threshold, a malformed ACK or a rejection. */
int32_t cy8c4046fni_write_gesture_cfg_55b400(const g2_touch_ops_t *ops, const uint16_t *threshold)
{
    uint8_t body[2];
    uint8_t ack[3];
    int32_t ret;

    audio_uart_buffer_zero(body, sizeof(body), 0u);
    audio_uart_buffer_zero(ack, sizeof(ack), 0u);
    if (ops == NULL)
        return -1;
    if (cy8c4046fni_gesture_cfg_valid_55b3ea(threshold) == 0u)
        return 0xff;
    body[0] = (uint8_t)*threshold;
    body[1] = (uint8_t)(*threshold >> 8);
    ret = (int32_t)ops->cmd_write(G2_TOUCH_CMD_WRITE_GESTURE_CFG, body, 2u);
    if (ret != 0)
        return ret;
    ret = (int32_t)ops->read(ack, 3u);
    if (ret != 0)
        return ret;
    if (ack[0] != GESTURE_ACK_ID || ack[2] != GESTURE_ACK_END) {
        TOUCH_LOG(1u, 3u, 0xdcu, fn_write_gesture_cfg, ack_invalid, ack_invalid_short,
                  ack[0], ack[1], ack[2]);
        return 0xff;
    }
    if (ack[1] != 0u) {
        TOUCH_LOG(1u, 1u, 0xe1u, fn_write_gesture_cfg, write_rejected, write_rejected_short,
                  ack[1]);
        return 0xff;
    }
    return 0;
}

/* Stock 0x55b530 (_cy8c4046fniReadGestureCfg): command 8, u16 LE reply.
 * A zero threshold is reported as invalid (0xff). */
int32_t cy8c4046fni_read_gesture_cfg_55b530(const g2_touch_ops_t *ops, uint16_t *threshold)
{
    uint8_t rx[2];
    int32_t ret;

    audio_uart_buffer_zero(rx, sizeof(rx), 0u);
    if (ops == NULL || threshold == NULL)
        return -1;
    ret = (int32_t)ops->cmd_read(G2_TOUCH_CMD_READ_GESTURE_CFG, rx, 2u);
    if (ret != 0)
        return ret;
    *threshold = (uint16_t)(rx[0] | (rx[1] << 8));
    if (cy8c4046fni_gesture_cfg_valid_55b3ea(threshold) == 0u) {
        TOUCH_LOG(1u, 1u, 0xf9u, fn_read_gesture_cfg, cfg_invalid, cfg_invalid_short,
                  *threshold);
        return 0xff;
    }
    return 0;
}

/* Stock 0x55b5e4: send command 2; the touch firmware writes its mailbox and
 * resets into the resident bootloader without a reliable ACK. */
int32_t DRV_TouchSwitch2Dfu_55b5e4(void)
{
    int32_t ret = cy8c4046fni_switch_to_dfu_55b340(&g2_touch_ops);

    if (ret == 0)
        return 0;
    TOUCH_LOG(1u, 1u, 0x10eu, fn_switch2dfu, switch2dfu_failed, switch2dfu_failed_short, ret);
    return -1;
}

/* Stock 0x55b676: command 3 (no-op on the touch side) followed by a 16-byte
 * read returns the last published event report. The transport status is
 * ignored; a failed read copies out zeros. */
void DRV_TouchReadReport_55b676(uint8_t report[16])
{
    uint8_t rx[16];

    audio_uart_buffer_zero(rx, sizeof(rx), 0u);
    if (report == NULL)
        return;
    (void)cy8c4046fni_read_report_55b35a(&g2_touch_ops, rx, 16u);
    (void)audio_queue_copy_bytes(report, rx, 16u);
}

/* Stock 0x55b730: command 5. */
int32_t DRV_TouchSaveProximityBaseline_55b730(void)
{
    int32_t ret = cy8c4046fni_save_baseline_55b38e(&g2_touch_ops);

    if (ret == 0)
        return 0;
    TOUCH_LOG(1u, 1u, 0x165u, fn_save_baseline, save_baseline_failed,
              save_baseline_failed_short, ret);
    return -1;
}

/* Stock 0x55b78a: command 6; 0xffff on failure. */
uint16_t DRV_TouchReadProximityBaseline_55b78a(void)
{
    uint16_t baseline = 0;
    int32_t ret = cy8c4046fni_read_baseline_55b3a8(&g2_touch_ops, &baseline);

    if (ret != 0) {
        TOUCH_LOG(1u, 1u, 0x175u, fn_read_baseline, read_baseline_failed,
                  read_baseline_failed_short, ret);
        return 0xffffu;
    }
    TOUCH_LOG(3u, 2u, 0x179u, fn_read_baseline, read_baseline_ok, read_baseline_ok_short,
              baseline, baseline);
    return baseline;
}

int32_t DRV_TouchWriteGestureCfg_55b840(const uint16_t *threshold)
{
    int32_t ret = cy8c4046fni_write_gesture_cfg_55b400(&g2_touch_ops, threshold);

    if (ret == 0) {
        TOUCH_LOG(3u, 1u, 0x18cu, fn_drv_write_gesture_cfg, write_cfg_ok, write_cfg_ok_short,
                  *threshold);
        return 0;
    }
    if (threshold != NULL)
        TOUCH_LOG(1u, 2u, 0x185u, fn_drv_write_gesture_cfg, write_cfg_failed,
                  write_cfg_failed_short, *threshold, ret);
    else
        TOUCH_LOG(1u, 1u, 0x187u, fn_drv_write_gesture_cfg, write_cfg_null,
                  write_cfg_null_short, ret);
    return -1;
}

int32_t DRV_TouchReadGestureCfg_55b92a(uint16_t *threshold)
{
    int32_t ret = cy8c4046fni_read_gesture_cfg_55b530(&g2_touch_ops, threshold);

    if (ret == 0) {
        TOUCH_LOG(3u, 1u, 0x19au, fn_drv_read_gesture_cfg, read_cfg_ok, read_cfg_ok_short,
                  *threshold);
        return 0;
    }
    TOUCH_LOG(1u, 1u, 0x196u, fn_drv_read_gesture_cfg, read_cfg_failed, read_cfg_failed_short,
              ret);
    return -1;
}
