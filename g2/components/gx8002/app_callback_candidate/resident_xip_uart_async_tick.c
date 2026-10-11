/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10208334: UART asynchronous dequeue/CRC/handler dispatch.
 * Native disassembly establishes the 32-byte packet, 16 x 28-byte dispatch
 * records, callback offsets, and the three inline literal addresses.
 */
#include <stdint.h>
#include <stddef.h>

extern int32_t gx8002_xip_tws_dequeue_10206fb0(
    volatile void *queue, uint32_t *packet);
extern uint32_t crc32(uint32_t crc, const unsigned char *data, unsigned int len);
extern void gx8002_xip_tws_publish_10206c24(const char *format, ...);

struct gx8002_xip_uart_dispatch {
    uint8_t command;
    uint8_t reserved[3];
    uint32_t subtype;
    uint32_t fields_08_13[3];
    uint32_t callback;
    uint32_t context;
};
_Static_assert(sizeof(struct gx8002_xip_uart_dispatch) == 28,
               "native UART dispatch stride");

uint32_t gx8002_xip_uart_async_tick_10208334(void)
{
    uint32_t packet[8];
    if (gx8002_xip_tws_dequeue_10206fb0(
            (volatile void *)(uintptr_t)UINT32_C(0x2002ecc4), packet) == 0)
        return UINT32_MAX;

    uint8_t *const bytes = (uint8_t *)packet;
    uint32_t length = packet[6];
    if (bytes[7] == 1u &&
        crc32(0u, (const unsigned char *)(uintptr_t)packet[4], length)
            != packet[7]) {
        /* Exact authenticated XIP literal at 0x1020b17d. */
        gx8002_xip_tws_publish_10206c24("Crc Error %d\n", length);
        return UINT32_MAX;
    }

    volatile const struct gx8002_xip_uart_dispatch *const table =
        (volatile const struct gx8002_xip_uart_dispatch *)(uintptr_t)
            UINT32_C(0x2002e360);
    uint16_t subtype = (uint16_t)(bytes[4] | ((uint16_t)bytes[5] << 8));
    uint8_t command = bytes[20];
    for (uint32_t index = 0u; index < 16u; ++index) {
        volatile const struct gx8002_xip_uart_dispatch *const row = &table[index];
        if (row->subtype == subtype && row->command == command) {
            uint32_t (*callback)(const uint32_t *, uint32_t) =
                (uint32_t (*)(const uint32_t *, uint32_t))(uintptr_t)row->callback;
            return callback(packet, row->context);
        }
    }
    return UINT32_MAX;
}
