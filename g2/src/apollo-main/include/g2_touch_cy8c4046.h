/* Infineon PSoC 4000T (CY8C4046FNI-T412) touch controller, Apollo side
 * (stock driver\touch\drv_cy8c4046fni.c, native 0x55b2ec..0x55b9c5).
 *
 * The controller is an I2C slave on product bus 5, 7-bit address 0x0c. A
 * host command is one command byte, optionally followed by a body in the
 * same write; a reply is read back with a repeated-start transfer. The
 * touch-side command handlers are in g2/src/touch (see
 * g2/docs/reference/findings-touch-case.md section 1.4):
 *   1 read version (4 B, big-endian on the wire)     2 enter DFU (no reply)
 *   3 read the last 16-byte event report             4 read sensor diffs (10 B)
 *   5 save proximity baseline (deferred)            6 read saved baseline (u16 LE)
 *   7 write long-press threshold (u16 LE, ACK 07 xx 17) 8 read the threshold (u16 LE)
 *
 * All transport goes through the four-entry table at RAM 0x20073e24, which
 * the touch-DFU service reuses for its raw bootloader frames. */
#ifndef G2_TOUCH_CY8C4046_H
#define G2_TOUCH_CY8C4046_H

#include <stdint.h>

#define G2_TOUCH_I2C_BUS  5u
#define G2_TOUCH_I2C_ADDR 0x0cu

enum {
    G2_TOUCH_CMD_READ_VERSION        = 1u,
    G2_TOUCH_CMD_ENTER_DFU           = 2u,
    G2_TOUCH_CMD_READ_REPORT         = 3u,
    G2_TOUCH_CMD_READ_SENSOR_DIFF    = 4u,
    G2_TOUCH_CMD_SAVE_BASELINE       = 5u,
    G2_TOUCH_CMD_READ_BASELINE       = 6u,
    G2_TOUCH_CMD_WRITE_GESTURE_CFG   = 7u,
    G2_TOUCH_CMD_READ_GESTURE_CFG    = 8u,
};

/* Transport table (RAM 0x20073e24, 16 bytes, filled from ROM pointers
 * 0x55b2ed/0x55b305/0x55b31d/0x55b32f). Every entry returns the I2C HAL
 * status: 0 ok, 1 failure. */
typedef struct {
    uint32_t (*cmd_write)(uint8_t cmd, const void *body, uint16_t len); /* +0x0 joined write */
    uint32_t (*cmd_read)(uint8_t cmd, void *rx, uint16_t len);         /* +0x4 write cmd, read rx */
    uint32_t (*write)(const void *tx, uint16_t len);                   /* +0x8 raw write */
    uint32_t (*read)(void *rx, uint16_t len);                          /* +0xc raw read */
} g2_touch_ops_t;
_Static_assert(sizeof(g2_touch_ops_t) == 16, "stock transport table is 16 bytes");

extern g2_touch_ops_t g2_touch_ops; /* RAM 0x20073e24 */

uint32_t cy8c4046fni_i2c_write_55b31c(const void *tx, uint16_t len);
uint32_t cy8c4046fni_i2c_read_55b32e(void *rx, uint16_t len);
int32_t cy8c4046fni_write_gesture_cfg_55b400(const g2_touch_ops_t *ops, const uint16_t *threshold);
int32_t cy8c4046fni_read_gesture_cfg_55b530(const g2_touch_ops_t *ops, uint16_t *threshold);
int32_t DRV_TouchSwitch2Dfu_55b5e4(void);
void DRV_TouchReadReport_55b676(uint8_t report[16]);
int32_t DRV_TouchSaveProximityBaseline_55b730(void);
uint16_t DRV_TouchReadProximityBaseline_55b78a(void);
int32_t DRV_TouchWriteGestureCfg_55b840(const uint16_t *threshold);
int32_t DRV_TouchReadGestureCfg_55b92a(uint16_t *threshold);

#endif
