/* SPDX-License-Identifier: MIT */
#include <stdint.h>

typedef void (*uart_ready_callback)(uint32_t, uint32_t, void *);
typedef void (*uart_done_callback)(uint32_t, void *);

#ifdef OPEN_CFW_GX8002_BACKUP_SPLIT_TX
/* Kept separate to fit the fixed backup interrupt entry. The linker places
 * this complete helper after the complete source-built FIFO routine. */
__attribute__((noinline)) static void uart_write_bytes(volatile uint32_t *device,
                                                       uint32_t buffer, uint32_t count)
{
    for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i)
        device[0] = *(uint8_t *)(uintptr_t)(buffer + i);
}
#endif

/* Recovered from codec package 0xc804..0xc8ec. Admission requires decoded
 * trace qualification, including callbacks and the transmitter drain loop. */
int open_cfw_gx8002_uart_interrupt(int irq, void *private_data)
{
    (void)irq;
    volatile uint32_t *d = private_data;
    volatile uint32_t *device = (volatile uint32_t *)(uintptr_t)d[1];
    uint32_t pending = device[2];
    if (pending & 4u) {
#ifdef OPEN_CFW_GX8002_BACKUP_RX_ORDER
        /* Backup stock reads descriptor mode before the hardware count. */
        uint32_t mode = d[16];
        uint32_t available = device[0x21];
#else
        uint32_t available = device[0x21];
        uint32_t mode = d[16];
#endif
        if (mode == 1) {
            uart_ready_callback callback = (uart_ready_callback)(uintptr_t)d[20];
            void *context = (void *)(uintptr_t)d[21];
            callback(d[0], available, context);
        } else if (!d[11] && mode == 2) {
            uint32_t remaining = d[25];
            uint32_t buffer = d[24];
            uint32_t count = available < remaining ? available : remaining;
#ifdef OPEN_CFW_GX8002_BACKUP_RX_ORDER
            if ((int32_t)count > 0) {
                uint8_t *cursor = (uint8_t *)(uintptr_t)buffer;
                uint8_t *end = cursor + count;
                volatile uint32_t *current = device;
                for (;;) {
                    *cursor++ = (uint8_t)current[0];
                    if (cursor == end) break;
                    current = (volatile uint32_t *)(uintptr_t)d[1];
                }
                buffer = d[24];
                remaining = d[25];
            }
            d[24] = buffer + count;
            uint32_t left = remaining - count;
#else
            for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i) {
                volatile uint32_t *current = (volatile uint32_t *)(uintptr_t)d[1];
                *(uint8_t *)(uintptr_t)(buffer + i) = (uint8_t)current[0];
            }
            d[24] = d[24] + count;
            uint32_t left = d[25] - count;
#endif
            d[25] = left;
            if (!left) {
                volatile uint32_t *current = (volatile uint32_t *)(uintptr_t)d[1];
                void *context = (void *)(uintptr_t)d[23];
                current[1] = current[1] & ~1u;
                uint32_t port = d[0];
                uart_done_callback callback = (uart_done_callback)(uintptr_t)d[22];
                callback(port, context);
            }
        }
    }
    if (pending & 2u) {
        device = (volatile uint32_t *)(uintptr_t)d[1];
        uint32_t used = device[0x20];
        uint32_t parameter = device[0x3d];
        uint32_t available = (((parameter >> 16) & 255u) << 4) - used;
        uint32_t mode = d[17];
        if (mode == 1) {
            uart_ready_callback callback = (uart_ready_callback)(uintptr_t)d[18];
            void *context = (void *)(uintptr_t)d[19];
            callback(d[0], available, context);
        } else if (!d[11] && mode == 2) {
            uint32_t remaining = d[30];
            uint32_t count = available < remaining ? available : remaining;
            uint32_t buffer = d[29];
#ifdef OPEN_CFW_GX8002_BACKUP_SPLIT_TX
            uart_write_bytes(device, buffer, count);
#else
            for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i)
                device[0] = *(uint8_t *)(uintptr_t)(buffer + i);
#endif
#ifdef OPEN_CFW_GX8002_BACKUP_RX_ORDER
            if ((int32_t)count > 0) remaining = d[30];
#endif
            d[29] = buffer + count;
#ifdef OPEN_CFW_GX8002_BACKUP_RX_ORDER
            uint32_t left = remaining - count;
#else
            uint32_t left = d[30] - count;
#endif
            d[30] = left;
            if (!left) {
                while (!(device[5] & 64u)) {}
                device[1] = device[1] & ~2u;
                void *context = (void *)(uintptr_t)d[28];
                uart_done_callback callback = (uart_done_callback)(uintptr_t)d[27];
                callback(d[0], context);
            }
        }
    }
    return 0;
}
