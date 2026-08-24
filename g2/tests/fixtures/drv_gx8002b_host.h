#ifndef OPEN_CFW_DRV_GX8002B_HOST_H
#define OPEN_CFW_DRV_GX8002B_HOST_H
#include <stdbool.h>
#include <stdint.h>

extern uint32_t host_gx_iser[16];
extern uint32_t host_gx_icer[16];
extern uint8_t host_gx_ipr[512];
extern uint8_t host_gx_shpr_storage[32];
extern uint8_t host_gx_power_state;
extern uint8_t host_gx_i2s_state;
extern void *host_gx_i2s_handle;
extern uint8_t host_gx_config;
extern uint8_t host_gx_transfer;
extern int16_t host_gx_irq;

#define OPEN_CFW_GX_NVIC_ISER host_gx_iser
#define OPEN_CFW_GX_NVIC_ICER host_gx_icer
#define OPEN_CFW_GX_NVIC_IPR host_gx_ipr
#define OPEN_CFW_GX_NVIC_SHPR (host_gx_shpr_storage + 4)
#define OPEN_CFW_GX_DSB() host_gx_dsb()
#define OPEN_CFW_GX_ISB() host_gx_isb()
#define OPEN_CFW_GX_POWER_STATE host_gx_power_state
#define OPEN_CFW_GX_I2S_STATE host_gx_i2s_state
#define OPEN_CFW_GX_I2S_HANDLE host_gx_i2s_handle
#define OPEN_CFW_GX_I2S_CONFIG ((void *)&host_gx_config)
#define OPEN_CFW_GX_I2S_TRANSFER ((void *)&host_gx_transfer)
#define OPEN_CFW_GX_I2S_IRQ host_gx_irq

void host_gx_dsb(void);
void host_gx_isb(void);
void host_gx_gpio_write(uint32_t index, uint32_t value);
uint32_t host_gx_delay(uint32_t milliseconds);
void host_gx_board_i2s_init(uint32_t instance, uint8_t alternate);
void host_gx_board_i2s_deinit(uint32_t instance, uint8_t alternate);
void host_gx_irq_enable_global(void);
uint32_t host_gx_i2s_initialize(uint32_t module, void **handle);
uint32_t host_gx_i2s_deinitialize(void *handle);
uint32_t host_gx_i2s_power_control(void *handle, uint32_t state, bool retain);
uint32_t host_gx_i2s_configure(void *handle, void *config);
uint32_t host_gx_i2s_enable(void *handle);
uint32_t host_gx_i2s_disable(void *handle);
uint32_t host_gx_i2s_dma_configure(void *handle, void *config, void *transfer);
uint32_t host_gx_i2s_dma_start(void *handle, void *config);
uint32_t host_gx_i2s_dma_get_buffer(void *handle, uint32_t direction);
uint32_t host_gx_i2s_interrupt_status(void *handle, uint32_t *status,
    bool enabled_only);
uint32_t host_gx_i2s_interrupt_clear(void *handle, uint32_t status);
uint32_t host_gx_i2s_interrupt_service(void *handle, uint32_t status,
    void *config);
uint32_t host_gx_cache_invalidate(void *descriptor, uint32_t clean);
void host_gx_rx_notify(void);
void host_gx_audio_notify(void);
void host_gx_nvic_enable(int32_t irq);
void host_gx_nvic_disable(int32_t irq);
void host_gx_nvic_set_priority(int32_t irq, uint32_t priority);
void host_gx_power_on(void);
void host_gx_power_off(void);

#define OPEN_CFW_GX_GPIO_WRITE(i, v) host_gx_gpio_write((i), (v))
#define OPEN_CFW_GX_DELAY(ms) host_gx_delay((ms))
#define OPEN_CFW_GX_BOARD_I2S_INIT(i, a) host_gx_board_i2s_init((i), (a))
#define OPEN_CFW_GX_BOARD_I2S_DEINIT(i, a) host_gx_board_i2s_deinit((i), (a))
#define OPEN_CFW_GX_IRQ_ENABLE_GLOBAL() host_gx_irq_enable_global()
#define OPEN_CFW_GX_I2S_INITIALIZE(m, h) host_gx_i2s_initialize((m), (h))
#define OPEN_CFW_GX_I2S_DEINITIALIZE(h) host_gx_i2s_deinitialize((h))
#define OPEN_CFW_GX_I2S_POWER_CONTROL(h, s, r) host_gx_i2s_power_control((h), (s), (r))
#define OPEN_CFW_GX_I2S_CONFIGURE(h, c) host_gx_i2s_configure((h), (c))
#define OPEN_CFW_GX_I2S_ENABLE(h) host_gx_i2s_enable((h))
#define OPEN_CFW_GX_I2S_DISABLE(h) host_gx_i2s_disable((h))
#define OPEN_CFW_GX_I2S_DMA_CONFIGURE(h, c, t) host_gx_i2s_dma_configure((h), (c), (t))
#define OPEN_CFW_GX_I2S_DMA_START(h, c) host_gx_i2s_dma_start((h), (c))
#define OPEN_CFW_GX_I2S_DMA_GET_BUFFER(h, d) host_gx_i2s_dma_get_buffer((h), (d))
#define OPEN_CFW_GX_I2S_INTERRUPT_STATUS(h, s, e) host_gx_i2s_interrupt_status((h), (s), (e))
#define OPEN_CFW_GX_I2S_INTERRUPT_CLEAR(h, s) host_gx_i2s_interrupt_clear((h), (s))
#define OPEN_CFW_GX_I2S_INTERRUPT_SERVICE(h, s, c) host_gx_i2s_interrupt_service((h), (s), (c))
#define OPEN_CFW_GX_CACHE_INVALIDATE(d, c) host_gx_cache_invalidate((d), (c))
#define OPEN_CFW_GX_RX_NOTIFY() host_gx_rx_notify()
#define OPEN_CFW_GX_AUDIO_NOTIFY() host_gx_audio_notify()
#define OPEN_CFW_GX_NVIC_ENABLE(i) host_gx_nvic_enable((i))
#define OPEN_CFW_GX_NVIC_DISABLE(i) host_gx_nvic_disable((i))
#define OPEN_CFW_GX_NVIC_SET_PRIORITY(i, p) host_gx_nvic_set_priority((i), (p))
#define OPEN_CFW_GX_POWER_ON() host_gx_power_on()
#define OPEN_CFW_GX_POWER_OFF() host_gx_power_off()
#endif
