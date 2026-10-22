/* Board UART channel layer: the three bodies that had no C.
 * Same 28-byte channel records at RAM 0x20000d2c (literal 0x55e98c) as
 * hal/uart/uart-channel/uart_channel.c, hal/u-07/hal_uart_start_55e68e.c and
 * drivers/codec-host/codec-uart-lifecycle/lifecycle.c.
 *
 *   0x55e262..0x55e287  NVIC_DisableIRQ (ICER 0xe000e180, literal 0x55e97c)
 *   0x55e75a..0x55e7f9  channel stop
 *   0x55e956..0x55e975  channel TX flush
 *
 * Callers: drivers/power/box-detect/box_uart_mgr.c. */
#include <stdint.h>

#define UART_CHANNELS 4u
#define UART_IRQ_BASE 15
#define UART_INT_MASK 0x471u /* the set re-enabled by hal_uart_start_55e68e */
#define NVIC_ICER 0xe000e180u

typedef struct {
    uint32_t rx_pin; /* +0x0 */
    uint32_t tx_pin; /* +0x4 */
    uint32_t rx_cfg; /* +0x8 am_hal_gpio_pincfg_t */
    uint32_t tx_cfg; /* +0xc */
} g2_uart_stop_pins_t;

typedef struct {
    uint32_t module;                   /* +0x00 UART instance, IRQ = module + 15 */
    void *handle;                      /* +0x04 HAL handle */
    const g2_uart_stop_pins_t *pins;   /* +0x08 */
    const uint32_t *config;            /* +0x0c */
    void *rx;                          /* +0x10 */
    void (*callback)(uint8_t *, uint32_t); /* +0x14 */
    uint8_t active;                    /* +0x18 */
    uint8_t tx_done;                   /* +0x19 */
    uint8_t pad[2];
} g2_uart_stop_channel_t;
_Static_assert(sizeof(g2_uart_stop_channel_t) == 28, "channel record is 28 bytes");

extern g2_uart_stop_channel_t g2_uart_channels[UART_CHANNELS]; /* RAM 0x20000d2c */
extern const uint32_t g2_audio_clock_pin_config;                /* ROM 0x78ee48 (value 3), literal 0x55e994 */

extern uint32_t am_hal_uart_interrupt_disable(void *handle, uint32_t mask); /* 0x58e7ae */
extern uint32_t am_hal_uart_tx_flush(void *handle);                        /* 0x58e6de */
extern uint32_t uart_rx_drain_58e352(void *handle);                        /* am_hal_uart_rx_fifo_drain */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern void g2_delay_us_491102(uint32_t microseconds);
extern void nvic_clear_pending_irq_55e288(int16_t irq);

void nvic_disable_irq_55e262(int16_t irq);
uint32_t hal_uart_stop_55e75a(uint8_t uart);
uint32_t hal_uart_tx_flush_55e956(uint8_t uart);

/* Stock 0x55e262: CMSIS NVIC_DisableIRQ, followed by DSB/ISB. */
void nvic_disable_irq_55e262(int16_t irq)
{
    if (irq >= 0) {
        ((volatile uint32_t *)(uintptr_t)NVIC_ICER)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
        __asm volatile("dsb 0xf" ::: "memory");
        __asm volatile("isb 0xf" ::: "memory");
    }
}

/* Stock 0x55e75a: disable the channel's UART interrupts, clear and disable
 * its NVIC line, drain the RX FIFO, then park the TX pin on the ROM pad
 * config and restore the RX pin config (10 us settle after each). Returns 1
 * for an invalid channel or when the interrupt disable failed, else 0. The
 * active flag is left unchanged. */
uint32_t hal_uart_stop_55e75a(uint8_t uart)
{
    if (uart >= UART_CHANNELS)
        return 1u;

    uint32_t err = am_hal_uart_interrupt_disable(g2_uart_channels[uart].handle, UART_INT_MASK);
    nvic_clear_pending_irq_55e288((int16_t)(g2_uart_channels[uart].module + UART_IRQ_BASE));
    nvic_disable_irq_55e262((int16_t)(g2_uart_channels[uart].module + UART_IRQ_BASE));
    (void)uart_rx_drain_58e352(g2_uart_channels[uart].handle);

    (void)am_hal_gpio_pinconfig_480f0c(g2_uart_channels[uart].pins->tx_pin, g2_audio_clock_pin_config);
    g2_delay_us_491102(10u);
    (void)am_hal_gpio_pinconfig_480f0c(g2_uart_channels[uart].pins->rx_pin,
                                       g2_uart_channels[uart].pins->rx_cfg);
    g2_delay_us_491102(10u);

    return err != 0u ? 1u : 0u;
}

/* Stock 0x55e956: wait for the channel's TX FIFO to drain. Returns 1 for an
 * invalid channel, else the HAL status. */
uint32_t hal_uart_tx_flush_55e956(uint8_t uart)
{
    if (uart >= UART_CHANNELS)
        return 1u;
    return am_hal_uart_tx_flush(g2_uart_channels[uart].handle);
}
