/* Shared uLED panel MSPI request record and RAM cells, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\uled\drv_mspi_uled_common.c.
 *
 * Every panel helper fills one 28-byte request (from a ROM template) and hands
 * it to am_devices_mspi_read / _write / _qspi_write / _qspi_write_async
 * (0x59cc40 / 0x59ccdc / 0x59cd86 / 0x59ce1e). mspi_transfer_build (0x59cafc)
 * converts it into the 24-byte am_hal_mspi_pio_transfer_t (IAR one-byte enum
 * layout): +0 NumBytes, +5 DCX, +6 eDirection, +7 bSendAddr, +8 DeviceAddr,
 * +12 bSendInstr, +14 ui16DeviceInstr, +16 bTurnaround, +17 bEnWRLatency,
 * +20 pui32Buffer. uled_rw_param_validate (0x59cb42) rejects a NULL request,
 * a NULL handle (+24) and a NULL buffer (+20). */
#ifndef G2_ULED_MSPI_REQUEST_H
#define G2_ULED_MSPI_REQUEST_H

#include <stdint.h>

typedef struct {
    uint8_t send_addr;   /* +0x00 -> PIO bSendAddr */
    uint8_t pad1[3];
    uint32_t dev_addr;   /* +0x04 -> PIO ui32DeviceAddr (QSPI address phase) */
    uint8_t send_instr;  /* +0x08 -> PIO bSendInstr */
    uint8_t instr;       /* +0x09 -> PIO ui16DeviceInstr (low byte) */
    uint8_t pad2[2];
    uint32_t num_bytes;  /* +0x0c */
    uint8_t turnaround;  /* +0x10 -> PIO bTurnaround (dummy cycles) */
    uint8_t pad3[3];
    void *buffer;        /* +0x14 */
    void *handle;        /* +0x18 am_hal_mspi handle */
} g2_uled_mspi_request_t;
_Static_assert(sizeof(g2_uled_mspi_request_t) == 0x1c, "stock uLED MSPI request is 28 bytes");

/* MSPI device layer, drv_mspi_uled_common.c. */
extern uint32_t display_driver_uled_type0_packet_59cc40(void *request);       /* 0x59cc40 am_devices_mspi_read */
extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *request); /* 0x59ccdc am_devices_mspi_write */
extern uint32_t am_devices_mspi_qspi_write(g2_uled_mspi_request_t *request);  /* 0x59cd86 */
extern uint32_t display_driver_uled_qspi_write_async_59ce1e(const void *request); /* 0x59ce1e */

/* Panel RAM cells written by am_devices_mspi_*_init. */
extern void *g2_jbd4010_mspi_handle;   /* RAM 0x20074524 */
extern uint8_t *g2_jbd4010_framebuffer; /* RAM 0x20074528, 640x480 4-bpp (0x140 bytes per row) */
extern void *g2_a6ng_mspi_handle;      /* RAM 0x20074510 */
extern uint8_t *g2_a6ng_framebuffer;    /* RAM 0x20074514, 640x480 4-bpp */

#define G2_ULED_WIDTH  640
#define G2_ULED_HEIGHT 480

#endif
