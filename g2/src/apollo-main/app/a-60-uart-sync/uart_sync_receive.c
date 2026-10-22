/* Left/right sync UART receive path, native 0x584b3c..0x584bbf (literal pool
 * 0x584e48..0x584e74 shared with the rest of the sync UART unit 0x5849d4..
 * 0x584e93). Stock source file not named by a string; the unit drives UART0
 * (0x40039000, IRQ 15) for the glasses' left/right sync link.
 *
 * Called from the UART0 handler uart_sync_irq_handler_584a7c with (0x20, 1)
 * for RX and RX-timeout interrupts. Bytes accumulate in a 1 KiB staging buffer;
 * when the next read would not fit, the buffered bytes are first handed to the
 * receive callback (installed by audio_uart_sync_reset1 0x584c8c, normally
 * audio_uart_sync_callback 0x5417a4). With flush != 0 the buffer is handed
 * over and emptied after the read. Returns the number of bytes read now. */
#include <stdint.h>
#include <stddef.h>

#define UART_SYNC_RX_BUFFER_SIZE 0x400u

typedef void (*g2_uart_sync_rx_callback_t)(const void *bytes, uint32_t length);

extern void *g2_uart_sync_driver;                     /* RAM 0x20074610 */
extern uint32_t g2_uart_sync_rx_length;               /* RAM 0x20074614: bytes staged */
extern void (*g2_uart_sync_callback_cell)(void);      /* RAM 0x20074618: really g2_uart_sync_rx_callback_t */
extern uint8_t g2_uart_sync_rx_buffer[UART_SYNC_RX_BUFFER_SIZE]; /* RAM 0x2037a1a0 */

/* am_hal_uart FIFO read (0x58e2d8): reads up to length bytes, *received = count. */
extern uint32_t codec_fifo_read(const void *handle, uint8_t *buffer, uint32_t length, uint32_t *received);

uint32_t uart_sync_receive_584b3c(uint32_t max_len, uint32_t flush);

uint32_t uart_sync_receive_584b3c(uint32_t max_len, uint32_t flush)
{
    uint32_t received = 0u;
    uint32_t room = UART_SYNC_RX_BUFFER_SIZE - g2_uart_sync_rx_length;

    if (room < max_len) {
        if (g2_uart_sync_rx_length != 0u && g2_uart_sync_callback_cell != NULL)
            ((g2_uart_sync_rx_callback_t)(uintptr_t)g2_uart_sync_callback_cell)(g2_uart_sync_rx_buffer,
                                                                                g2_uart_sync_rx_length);
        g2_uart_sync_rx_length = 0u;
        room = UART_SYNC_RX_BUFFER_SIZE;
    }
    if (room < max_len)
        max_len = room;
    (void)codec_fifo_read(g2_uart_sync_driver, &g2_uart_sync_rx_buffer[g2_uart_sync_rx_length], max_len, &received);
    g2_uart_sync_rx_length += received;

    if ((uint8_t)flush != 0u) {
        if (g2_uart_sync_callback_cell != NULL && g2_uart_sync_rx_length != 0u)
            ((g2_uart_sync_rx_callback_t)(uintptr_t)g2_uart_sync_callback_cell)(g2_uart_sync_rx_buffer,
                                                                                g2_uart_sync_rx_length);
        g2_uart_sync_rx_length = 0u;
    }
    return received;
}
