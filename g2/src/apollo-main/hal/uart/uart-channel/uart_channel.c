/* Board UART channel layer (four channel records over the AmbiqSuite UART
 * HAL). Native 0x55e244..0x55e2a5, 0x55e2a6..0x55e2cd, 0x55e346..0x55e4eb and
 * 0x55e90c..0x55e955; literal pool 0x55e978..0x55e998.
 *
 * Channel records live at RAM 0x20000d2c, 28 bytes each:
 *   +0 UART module (IRQ = module + 15), +4 HAL handle, +8 pin table
 *   {rx_pin, tx_pin, rx_cfg, tx_cfg}, +12 UART config, +16 RX queue
 *   descriptor {.., .., count +8, buffer +12}, +20 RX callback, +24 active,
 *   +25 TX-complete flag.
 * The other channel functions (IRQ body 0x55e2ce, RX delivery 0x55e4ec,
 * enable 0x55e5bc, disable 0x55e630, TX 0x55e7fa, baud 0x55e898, callback
 * 0x55e8f0) are reconstructed in drivers/codec-host. */
#include <stdint.h>
#include <stddef.h>

#define UART_CHANNELS 4u
#define UART_IRQ_BASE 15
#define UART_INT_MASK 0x471u /* RX | RXTO | TXCMP | ... enabled at init */
#define UART_RX_BUFFER_SIZE 0x400u

#define NVIC_ISER 0xe000e100u
#define NVIC_ICPR 0xe000e280u
#define NVIC_IP   0xe000e400u
#define SCB_SHP   0xe000ed18u

typedef struct {
    uint32_t rx_pin;  /* +0x0 */
    uint32_t tx_pin;  /* +0x4 */
    uint32_t rx_cfg;  /* +0x8 am_hal_gpio_pincfg_t */
    uint32_t tx_cfg;  /* +0xc */
} g2_uart_pins_t;

typedef struct {
    uint32_t w0;      /* +0x0 passed to the buffer setup as its size */
    uint32_t w1;      /* +0x4 passed to the buffer setup as its pointer */
    uint32_t count;   /* +0x8 bytes received so far */
    uint8_t *buffer;  /* +0xc */
} g2_uart_queue_t;

typedef struct {
    uint32_t module;                  /* +0x00 */
    void *handle;                     /* +0x04 */
    const g2_uart_pins_t *pins;       /* +0x08 */
    const uint32_t *config;           /* +0x0c am_hal_uart_config_t */
    g2_uart_queue_t *rx;              /* +0x10 */
    void (*callback)(uint8_t *, uint32_t); /* +0x14 */
    uint8_t active;                   /* +0x18 */
    uint8_t tx_done;                  /* +0x19 */
    uint8_t pad[2];
} g2_uart_channel_t;
_Static_assert(sizeof(g2_uart_channel_t) == 28, "channel record is 28 bytes");

extern g2_uart_channel_t g2_uart_channels[UART_CHANNELS]; /* RAM 0x20000d2c */
extern const uint32_t g2_uart2_rx_pin_config;             /* ROM 0x78f104 (value 3) */

extern uint32_t audio_uart_sync_driver_bind(uint32_t module, void **handle);    /* 0x58dae4 am_hal_uart_initialize */
extern uint32_t codec_hal_power(uint32_t handle, uint32_t state, uint32_t retain); /* 0x58dbb8 am_hal_uart_power_control */
extern uint32_t codec_hal_configure(uint32_t handle, const uint32_t *config);    /* 0x58e09e am_hal_uart_configure */
extern uint32_t audio_uart_sync_driver_prepare(void *handle, uint32_t a, uint32_t b,
                                               uint32_t c, uint32_t d);          /* 0x58ddd6 buffer setup */
extern uint32_t audio_uart_sync_driver_baud(void *handle, uint32_t mask);        /* 0x58e782 interrupt enable */
extern uint32_t codec_gpio_config(uint32_t pin, uint32_t cfg);                   /* 0x480f0c am_hal_gpio_pinconfig */
extern uint32_t codec_uart_irq(uint32_t channel);                                /* 0x55e2ce */
extern uint32_t codec_channel_disable(uint32_t channel);                         /* 0x55e630 */
extern void *g2_memset_43bb00(void *dst, int32_t value, uint32_t len);           /* 0x43bb00 */
extern void uart_rx_drain_58e352(void *handle);                                  /* 0x58e352: fifo read of up to 32 bytes into NULL */

/* Stock 0x55e244: NVIC_EnableIRQ. */
void nvic_enable_irq_55e244(int16_t irq)
{
    if (irq >= 0)
        ((volatile uint32_t *)(uintptr_t)NVIC_ISER)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

/* Stock 0x55e288: NVIC_ClearPendingIRQ. */
void nvic_clear_pending_irq_55e288(int16_t irq)
{
    if (irq >= 0)
        ((volatile uint32_t *)(uintptr_t)NVIC_ICPR)[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

/* Stock 0x55e2a6: NVIC_SetPriority with 4 priority bits. */
void nvic_set_priority_55e2a6(int16_t irq, uint32_t priority)
{
    if (irq < 0)
        ((volatile uint8_t *)(uintptr_t)SCB_SHP)[((uint32_t)irq & 15u) - 4u] = (uint8_t)(priority << 4);
    else
        ((volatile uint8_t *)(uintptr_t)NVIC_IP)[irq] = (uint8_t)(priority << 4);
}

/* Stock 0x55e346/0x55e35c/0x55e372: UART1..3 vector handlers; only active
 * channels are serviced. */
void uart_channel1_isr_55e346(void)
{
    if (g2_uart_channels[1].active == 1u)
        (void)codec_uart_irq(1u);
}

void uart_channel2_isr_55e35c(void)
{
    if (g2_uart_channels[2].active == 1u)
        (void)codec_uart_irq(2u);
}

void uart_channel3_isr_55e372(void)
{
    if (g2_uart_channels[3].active == 1u)
        (void)codec_uart_irq(3u);
}

/* Stock 0x55e388: bring up every channel that has pins and a config, enable
 * its IRQ (priority 3 for channel 0, 4 otherwise) and UART interrupts, then
 * leave it shut down until a user enables it. Returns 1 if any HAL call
 * failed. */
uint32_t uart_channels_init_55e388(void)
{
    uint32_t err = 0u;

    for (uint32_t i = 0u; i < UART_CHANNELS; i++) {
        g2_uart_channel_t *c = &g2_uart_channels[i];
        if (c->pins == NULL || c->config == NULL)
            continue;

        err |= audio_uart_sync_driver_bind(c->module, &c->handle);
        if (i == 2u)
            err |= codec_gpio_config(c->pins->rx_pin, g2_uart2_rx_pin_config);
        else
            err |= codec_gpio_config(c->pins->rx_pin, c->pins->rx_cfg);
        err |= codec_gpio_config(c->pins->tx_pin, c->pins->tx_cfg);
        err |= codec_hal_power((uint32_t)(uintptr_t)c->handle, 0u, 0u);
        err |= codec_hal_configure((uint32_t)(uintptr_t)c->handle, c->config);
        err |= audio_uart_sync_driver_prepare(c->handle, c->rx->w1, c->rx->w0, 0u, 0u);

        int16_t irq = (int16_t)(c->module + UART_IRQ_BASE);
        nvic_clear_pending_irq_55e288(irq);
        nvic_set_priority_55e2a6(irq, i == 0u ? 3u : 4u);
        nvic_enable_irq_55e244(irq);
        err |= audio_uart_sync_driver_baud(c->handle, UART_INT_MASK);

        c->active = 1u;
        (void)codec_channel_disable(i);
    }
    return err != 0u ? 1u : 0u;
}

/* Stock 0x55e90c: drop buffered RX data and drain the hardware FIFO.
 * Returns 1 for an invalid channel, else 0. */
uint32_t uart_channel_rx_flush_55e90c(uint32_t channel)
{
    uint8_t ch = (uint8_t)channel;
    if (ch >= UART_CHANNELS)
        return 1u;
    g2_uart_channels[ch].rx->count = 0u;
    (void)g2_memset_43bb00(g2_uart_channels[ch].rx->buffer, 0, UART_RX_BUFFER_SIZE);
    uart_rx_drain_58e352(g2_uart_channels[ch].handle);
    return 0u;
}
