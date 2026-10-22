/* UART0 interrupt handler of the left/right sync link, native 0x584a7c..0x584b3b
 * (literal pool 0x584e48..0x584e67). Vector table entry 0x43807c (IRQ 15, UART0).
 * Runs only after the sync transport is bound (0x584bc0) and started.
 *
 * Interrupt bits (UART0 IES): RX (4) and RX timeout (6) run the receive path;
 * DMACP (11) clears RSR.DMACPL and wakes the writer; DMAER (12) stops the TX DMA,
 * marks a write error and wakes the writer; FE/PE/BE (7/8/9) only count. */
#include <stdint.h>
#include <stddef.h>

#define UART_INT_RX     (1u << 4)
#define UART_INT_RXTO   (1u << 6)
#define UART_INT_FE     (1u << 7)
#define UART_INT_PE     (1u << 8)
#define UART_INT_BE     (1u << 9)
#define UART_INT_DMACP  (1u << 11)
#define UART_INT_DMAER  (1u << 12)
#define UART0_RSR       0x40039004u
#define UART_RSR_DMACPL (1u << 4)

extern void *g2_uart_sync_driver;                   /* RAM 0x20074610 */
extern volatile uint8_t g2_uart_sync_started;       /* RAM 0x20074fc9 */
extern void *g2_uart_sync_semaphore_handle;         /* RAM 0x2007461c */
extern volatile uint8_t g2_uart_sync_write_error;   /* RAM 0x20074fca */
extern volatile uint32_t g2_uart_sync_break_errors;   /* RAM 0x2007462c */
extern volatile uint32_t g2_uart_sync_parity_errors;  /* RAM 0x20074628 */
extern volatile uint32_t g2_uart_sync_framing_errors; /* RAM 0x20074624 */
extern uint32_t am_hal_uart_interrupt_status_get_58e80e(void *handle, uint32_t *status, uint8_t enabled_only);
extern uint32_t am_hal_uart_interrupt_clear_58e7e4(void *handle, uint32_t status);
extern void uart_sync_receive_584b3c(uint32_t max_len, uint32_t from_isr);
extern void uart_sync_dma_stop_584a64(void);
extern int32_t osSemaphoreRelease(void *semaphore); /* 0x4499b8 */

void uart_sync_irq_handler_584a7c(void)
{
    uint32_t status = 0u;
    if (g2_uart_sync_driver == NULL || g2_uart_sync_started != 1u)
        return;
    (void)am_hal_uart_interrupt_status_get_58e80e(g2_uart_sync_driver, &status, 1u);
    (void)am_hal_uart_interrupt_clear_58e7e4(g2_uart_sync_driver, status);
    if (status & UART_INT_RX)
        uart_sync_receive_584b3c(0x20u, 1u);
    if (status & UART_INT_RXTO)
        uart_sync_receive_584b3c(0x20u, 1u);
    if (status & UART_INT_DMACP) {
        *(volatile uint32_t *)(uintptr_t)UART0_RSR &= ~UART_RSR_DMACPL;
        if (g2_uart_sync_semaphore_handle != NULL)
            (void)osSemaphoreRelease(g2_uart_sync_semaphore_handle);
    }
    if (status & UART_INT_DMAER) {
        uart_sync_dma_stop_584a64();
        g2_uart_sync_write_error = 1u;
        if (g2_uart_sync_semaphore_handle != NULL)
            (void)osSemaphoreRelease(g2_uart_sync_semaphore_handle);
    }
    if (status & UART_INT_BE)
        g2_uart_sync_break_errors++;
    if (status & UART_INT_PE)
        g2_uart_sync_parity_errors++;
    if (status & UART_INT_FE)
        g2_uart_sync_framing_errors++;
}
