/* Board UART channel start (re-arm after hal_uart_stop_55e75a).
 * Native 0x55e68e..0x55e75a; literal pool 0x55e98c (channel table) and
 * 0x55e994 (pin-config word). Companion of the channel layer in
 * hal/uart/uart-channel/uart_channel.c (same 28-byte channel records at
 * RAM 0x20000d2c); called by the box UART manager (box_uart_mgr.c). */
#include <stdint.h>

#define UART_CHANNELS 4u
#define UART_IRQ_BASE 15
#define UART_IRQ_PRIORITY 3u
#define UART_INT_MASK 0x471u /* same interrupt set enabled by uart_channels_init_55e388 */

typedef struct {
    uint32_t rx_pin;  /* +0x0 */
    uint32_t tx_pin;  /* +0x4 */
    uint32_t rx_cfg;  /* +0x8 */
    uint32_t tx_cfg;  /* +0xc */
} g2_uart_start_pins_t;

typedef struct {
    uint32_t module;                    /* +0x00 UART instance, IRQ = module + 15 */
    void *handle;                       /* +0x04 HAL handle */
    const g2_uart_start_pins_t *pins;   /* +0x08 */
    const uint32_t *config;             /* +0x0c */
    void *rx;                           /* +0x10 */
    void (*callback)(uint8_t *, uint32_t); /* +0x14 */
    uint8_t active;                     /* +0x18 */
    uint8_t tx_done;                    /* +0x19 */
    uint8_t pad[2];
} g2_uart_start_channel_t;
_Static_assert(sizeof(g2_uart_start_channel_t) == 28, "channel record is 28 bytes");

extern g2_uart_start_channel_t g2_uart_channels[UART_CHANNELS]; /* RAM 0x20000d2c */
extern const uint32_t g2_audio_clock_pin_config;                 /* ROM 0x78ee48 (value 3) */

extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern uint32_t uart_irq_fifo_drain(void *handle);               /* 0x58e352 */
extern void g2_delay_us_491102(uint32_t microseconds);
extern void nvic_clear_pending_irq_55e288(int16_t irq);
extern void nvic_set_priority_55e2a6(int16_t irq, uint32_t priority);
extern void nvic_enable_irq_55e244(int16_t irq);
extern uint32_t audio_uart_sync_driver_baud(void *handle, uint32_t mask); /* 0x58e782 interrupt enable */

/* Stock 0x55e68e: put the RX pin on the ROM pad config, drain the FIFO,
 * restore the TX pin config, drain again, then re-enable the UART IRQ
 * (priority 3) and interrupts and mark the channel active. Returns 1 for an
 * invalid channel or when the interrupt enable fails, else 0. The pin-config
 * results are ignored. */
uint32_t hal_uart_start_55e68e(uint8_t uart)
{
    uint32_t err = 0u;

    if (uart >= UART_CHANNELS)
        return 1u;
    g2_uart_start_channel_t *c = &g2_uart_channels[uart];

    (void)am_hal_gpio_pinconfig_480f0c(c->pins->rx_pin, g2_audio_clock_pin_config);
    (void)uart_irq_fifo_drain(c->handle);
    g2_delay_us_491102(10u);
    (void)am_hal_gpio_pinconfig_480f0c(c->pins->tx_pin, c->pins->tx_cfg);
    (void)uart_irq_fifo_drain(c->handle);
    g2_delay_us_491102(10u);

    nvic_clear_pending_irq_55e288((int16_t)(c->module + UART_IRQ_BASE));
    nvic_set_priority_55e2a6((int16_t)(c->module + UART_IRQ_BASE), UART_IRQ_PRIORITY);
    nvic_enable_irq_55e244((int16_t)(c->module + UART_IRQ_BASE));
    err |= audio_uart_sync_driver_baud(c->handle, UART_INT_MASK);

    c->active = 1u;
    return err != 0u ? 1u : 0u;
}
