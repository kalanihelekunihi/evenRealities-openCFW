/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of driver/codec/drv_gx8002b.c. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

#ifndef OPEN_CFW_GX_NVIC_ISER
#define OPEN_CFW_GX_NVIC_ISER \
    ((volatile uint32_t *)(uintptr_t)0xe000e100u)
#endif
#ifndef OPEN_CFW_GX_NVIC_ICER
#define OPEN_CFW_GX_NVIC_ICER \
    ((volatile uint32_t *)(uintptr_t)0xe000e180u)
#endif
#ifndef OPEN_CFW_GX_NVIC_IPR
#define OPEN_CFW_GX_NVIC_IPR \
    ((volatile uint8_t *)(uintptr_t)0xe000e400u)
#endif
#ifndef OPEN_CFW_GX_NVIC_SHPR
#define OPEN_CFW_GX_NVIC_SHPR \
    ((volatile uint8_t *)(uintptr_t)0xe000ed18u)
#endif
#ifndef OPEN_CFW_GX_DSB
#define OPEN_CFW_GX_DSB() __asm volatile ("dsb sy" ::: "memory")
#endif
#ifndef OPEN_CFW_GX_ISB
#define OPEN_CFW_GX_ISB() __asm volatile ("isb sy" ::: "memory")
#endif

#ifndef OPEN_CFW_GX_POWER_STATE
#define OPEN_CFW_GX_POWER_STATE \
    (*(volatile uint8_t *)(uintptr_t)0x20074fb6u)
#endif
#ifndef OPEN_CFW_GX_I2S_STATE
#define OPEN_CFW_GX_I2S_STATE \
    (*(volatile uint8_t *)(uintptr_t)0x20074fb7u)
#endif
#ifndef OPEN_CFW_GX_I2S_HANDLE
#define OPEN_CFW_GX_I2S_HANDLE \
    (*(void *volatile *)(uintptr_t)0x2007450cu)
#endif
#ifndef OPEN_CFW_GX_I2S_CONFIG
#define OPEN_CFW_GX_I2S_CONFIG ((void *)(uintptr_t)0x20000000u)
#endif
#ifndef OPEN_CFW_GX_I2S_TRANSFER
#define OPEN_CFW_GX_I2S_TRANSFER ((void *)(uintptr_t)0x20000740u)
#endif
#ifndef OPEN_CFW_GX_I2S_IRQ
#define OPEN_CFW_GX_I2S_IRQ \
    (*(volatile int16_t *)(uintptr_t)0x0078f558u)
#endif

#ifndef OPEN_CFW_GX_GPIO_WRITE
void open_cfw_gx_gpio_write(uint32_t index, uint32_t value);
#define OPEN_CFW_GX_GPIO_WRITE(index, value) \
    open_cfw_gx_gpio_write((index), (value))
#endif
#ifndef OPEN_CFW_GX_DELAY
uint32_t open_cfw_gx_delay(uint32_t milliseconds);
#define OPEN_CFW_GX_DELAY(milliseconds) \
    open_cfw_gx_delay((milliseconds))
#endif
#ifndef OPEN_CFW_GX_BOARD_I2S_INIT
void open_cfw_gx_board_i2s_init(uint32_t instance, uint8_t alternate);
#define OPEN_CFW_GX_BOARD_I2S_INIT(instance, alternate) \
    open_cfw_gx_board_i2s_init((instance), (alternate))
#endif
#ifndef OPEN_CFW_GX_BOARD_I2S_DEINIT
void open_cfw_gx_board_i2s_deinit(uint32_t instance, uint8_t alternate);
#define OPEN_CFW_GX_BOARD_I2S_DEINIT(instance, alternate) \
    open_cfw_gx_board_i2s_deinit((instance), (alternate))
#endif
#ifndef OPEN_CFW_GX_IRQ_ENABLE_GLOBAL
void open_cfw_gx_irq_enable_global(void);
#define OPEN_CFW_GX_IRQ_ENABLE_GLOBAL() open_cfw_gx_irq_enable_global()
#endif

#ifndef OPEN_CFW_GX_I2S_INITIALIZE
uint32_t open_cfw_gx_i2s_initialize(uint32_t module, void **handle);
#define OPEN_CFW_GX_I2S_INITIALIZE(module, handle) \
    open_cfw_gx_i2s_initialize((module), (handle))
#endif
#ifndef OPEN_CFW_GX_I2S_DEINITIALIZE
uint32_t open_cfw_gx_i2s_deinitialize(void *handle);
#define OPEN_CFW_GX_I2S_DEINITIALIZE(handle) \
    open_cfw_gx_i2s_deinitialize((handle))
#endif
#ifndef OPEN_CFW_GX_I2S_POWER_CONTROL
uint32_t open_cfw_gx_i2s_power_control(void *handle, uint32_t state,
    bool retain);
#define OPEN_CFW_GX_I2S_POWER_CONTROL(handle, state, retain) \
    open_cfw_gx_i2s_power_control((handle), (state), (retain))
#endif
#ifndef OPEN_CFW_GX_I2S_CONFIGURE
uint32_t open_cfw_gx_i2s_configure(void *handle, void *config);
#define OPEN_CFW_GX_I2S_CONFIGURE(handle, config) \
    open_cfw_gx_i2s_configure((handle), (config))
#endif
#ifndef OPEN_CFW_GX_I2S_ENABLE
uint32_t open_cfw_gx_i2s_enable(void *handle);
#define OPEN_CFW_GX_I2S_ENABLE(handle) open_cfw_gx_i2s_enable((handle))
#endif
#ifndef OPEN_CFW_GX_I2S_DISABLE
uint32_t open_cfw_gx_i2s_disable(void *handle);
#define OPEN_CFW_GX_I2S_DISABLE(handle) open_cfw_gx_i2s_disable((handle))
#endif
#ifndef OPEN_CFW_GX_I2S_DMA_CONFIGURE
uint32_t open_cfw_gx_i2s_dma_configure(void *handle, void *config,
    void *transfer);
#define OPEN_CFW_GX_I2S_DMA_CONFIGURE(handle, config, transfer) \
    open_cfw_gx_i2s_dma_configure((handle), (config), (transfer))
#endif
#ifndef OPEN_CFW_GX_I2S_DMA_START
uint32_t open_cfw_gx_i2s_dma_start(void *handle, void *config);
#define OPEN_CFW_GX_I2S_DMA_START(handle, config) \
    open_cfw_gx_i2s_dma_start((handle), (config))
#endif
#ifndef OPEN_CFW_GX_I2S_DMA_GET_BUFFER
uint32_t open_cfw_gx_i2s_dma_get_buffer(void *handle, uint32_t direction);
#define OPEN_CFW_GX_I2S_DMA_GET_BUFFER(handle, direction) \
    open_cfw_gx_i2s_dma_get_buffer((handle), (direction))
#endif
#ifndef OPEN_CFW_GX_I2S_INTERRUPT_STATUS
uint32_t open_cfw_gx_i2s_interrupt_status(void *handle, uint32_t *status,
    bool enabled_only);
#define OPEN_CFW_GX_I2S_INTERRUPT_STATUS(handle, status, enabled_only) \
    open_cfw_gx_i2s_interrupt_status((handle), (status), (enabled_only))
#endif
#ifndef OPEN_CFW_GX_I2S_INTERRUPT_CLEAR
uint32_t open_cfw_gx_i2s_interrupt_clear(void *handle, uint32_t status);
#define OPEN_CFW_GX_I2S_INTERRUPT_CLEAR(handle, status) \
    open_cfw_gx_i2s_interrupt_clear((handle), (status))
#endif
#ifndef OPEN_CFW_GX_I2S_INTERRUPT_SERVICE
uint32_t open_cfw_gx_i2s_interrupt_service(void *handle, uint32_t status,
    void *config);
#define OPEN_CFW_GX_I2S_INTERRUPT_SERVICE(handle, status, config) \
    open_cfw_gx_i2s_interrupt_service((handle), (status), (config))
#endif
#ifndef OPEN_CFW_GX_CACHE_INVALIDATE
uint32_t open_cfw_gx_cache_invalidate(void *descriptor, uint32_t clean);
#define OPEN_CFW_GX_CACHE_INVALIDATE(descriptor, clean) \
    open_cfw_gx_cache_invalidate((descriptor), (clean))
#endif
#ifndef OPEN_CFW_GX_RX_NOTIFY
void open_cfw_gx_rx_notify(void);
#define OPEN_CFW_GX_RX_NOTIFY() open_cfw_gx_rx_notify()
#endif
#ifndef OPEN_CFW_GX_AUDIO_NOTIFY
void open_cfw_gx_audio_notify(void);
#define OPEN_CFW_GX_AUDIO_NOTIFY() open_cfw_gx_audio_notify()
#endif

#ifndef OPEN_CFW_GX_NVIC_ENABLE
void open_cfw_gx8002_nvic_enable(int32_t irq);
#define OPEN_CFW_GX_NVIC_ENABLE(irq) open_cfw_gx8002_nvic_enable((irq))
#endif
#ifndef OPEN_CFW_GX_NVIC_DISABLE
void open_cfw_gx8002_nvic_disable(int32_t irq);
#define OPEN_CFW_GX_NVIC_DISABLE(irq) open_cfw_gx8002_nvic_disable((irq))
#endif
#ifndef OPEN_CFW_GX_NVIC_SET_PRIORITY
void open_cfw_gx8002_nvic_set_priority(int32_t irq, uint32_t priority);
#define OPEN_CFW_GX_NVIC_SET_PRIORITY(irq, priority) \
    open_cfw_gx8002_nvic_set_priority((irq), (priority))
#endif
#ifndef OPEN_CFW_GX_POWER_ON
void open_cfw_gx8002_power_on(void);
#define OPEN_CFW_GX_POWER_ON() open_cfw_gx8002_power_on()
#endif
#ifndef OPEN_CFW_GX_POWER_OFF
void open_cfw_gx8002_power_off(void);
#define OPEN_CFW_GX_POWER_OFF() open_cfw_gx8002_power_off()
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline))
void open_cfw_gx8002_nvic_enable(int32_t irq)
{
    int32_t signed_irq = (int16_t)irq;

    if (signed_irq >= 0) {
        uint32_t bit = 1u << ((uint32_t)irq & 31u);
        OPEN_CFW_GX_NVIC_ISER[(uint32_t)signed_irq >> 5] = bit;
    }
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used, noinline))
void open_cfw_gx8002_nvic_disable(int32_t irq)
{
    int32_t signed_irq = (int16_t)irq;

    if (signed_irq >= 0) {
        uint32_t bit = 1u << ((uint32_t)irq & 31u);
        OPEN_CFW_GX_NVIC_ICER[(uint32_t)signed_irq >> 5] = bit;
        OPEN_CFW_GX_DSB();
        OPEN_CFW_GX_ISB();
    }
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 3
__attribute__((used, noinline))
void open_cfw_gx8002_nvic_set_priority(int32_t irq, uint32_t priority)
{
    int32_t signed_irq = (int16_t)irq;
    uint8_t encoded = (uint8_t)(priority << 4);

    if (signed_irq >= 0) {
        OPEN_CFW_GX_NVIC_IPR[(uint32_t)signed_irq] = encoded;
    } else {
        uint32_t index = ((uint32_t)signed_irq & 15u) - 4u;
        OPEN_CFW_GX_NVIC_SHPR[index] = encoded;
    }
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
__attribute__((used, noinline))
void open_cfw_gx8002_i2s_isr(void)
{
    uint32_t status;
    void *handle = OPEN_CFW_GX_I2S_HANDLE;

    (void)OPEN_CFW_GX_I2S_INTERRUPT_STATUS(handle, &status, true);
    (void)OPEN_CFW_GX_I2S_INTERRUPT_CLEAR(handle, status);
    (void)OPEN_CFW_GX_I2S_INTERRUPT_SERVICE(handle, status,
        OPEN_CFW_GX_I2S_CONFIG);
    if ((status & 0x10u) != 0u) {
        OPEN_CFW_GX_RX_NOTIFY();
    }
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 5
__attribute__((used, noinline))
void open_cfw_gx8002_power_on(void)
{
    if (OPEN_CFW_GX_POWER_STATE != 0u) {
        return;
    }
    OPEN_CFW_GX_POWER_STATE = 1u;
    OPEN_CFW_GX_GPIO_WRITE(6u, 1u);
    (void)OPEN_CFW_GX_DELAY(5u);
    OPEN_CFW_GX_GPIO_WRITE(7u, 1u);
    (void)OPEN_CFW_GX_DELAY(20u);
    OPEN_CFW_GX_GPIO_WRITE(8u, 1u);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 6
__attribute__((used, noinline))
void open_cfw_gx8002_power_off(void)
{
    if (OPEN_CFW_GX_POWER_STATE == 0u) {
        return;
    }
    OPEN_CFW_GX_POWER_STATE = 0u;
    OPEN_CFW_GX_GPIO_WRITE(6u, 0u);
    OPEN_CFW_GX_GPIO_WRITE(7u, 0u);
    OPEN_CFW_GX_GPIO_WRITE(8u, 0u);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 7
__attribute__((used, noinline))
uint8_t open_cfw_gx8002_power_state_get(void)
{
    return OPEN_CFW_GX_POWER_STATE;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 8
__attribute__((used, noinline))
void open_cfw_gx8002_i2s_init(void)
{
    void *handle;

    if (OPEN_CFW_GX_I2S_STATE != 0u) {
        return;
    }
    OPEN_CFW_GX_I2S_STATE = 1u;
    OPEN_CFW_GX_BOARD_I2S_INIT(0u, 0u);
    (void)OPEN_CFW_GX_I2S_INITIALIZE(0u, (void **)&OPEN_CFW_GX_I2S_HANDLE);
    handle = OPEN_CFW_GX_I2S_HANDLE;
    (void)OPEN_CFW_GX_I2S_POWER_CONTROL(handle, 0u, false);
    (void)OPEN_CFW_GX_I2S_CONFIGURE(handle, OPEN_CFW_GX_I2S_CONFIG);
    (void)OPEN_CFW_GX_I2S_ENABLE(handle);
    (void)OPEN_CFW_GX_I2S_DMA_CONFIGURE(handle, OPEN_CFW_GX_I2S_CONFIG,
        OPEN_CFW_GX_I2S_TRANSFER);
    OPEN_CFW_GX_NVIC_SET_PRIORITY(OPEN_CFW_GX_I2S_IRQ, 4u);
    OPEN_CFW_GX_NVIC_ENABLE(OPEN_CFW_GX_I2S_IRQ);
    OPEN_CFW_GX_IRQ_ENABLE_GLOBAL();
    (void)OPEN_CFW_GX_I2S_DMA_START(handle, OPEN_CFW_GX_I2S_CONFIG);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 9
__attribute__((used, noinline))
void open_cfw_gx8002_i2s_deinit(void)
{
    void *handle;

    if (OPEN_CFW_GX_I2S_STATE == 0u) {
        return;
    }
    OPEN_CFW_GX_I2S_STATE = 0u;
    OPEN_CFW_GX_NVIC_DISABLE(OPEN_CFW_GX_I2S_IRQ);
    OPEN_CFW_GX_BOARD_I2S_DEINIT(0u, 0u);
    handle = OPEN_CFW_GX_I2S_HANDLE;
    (void)OPEN_CFW_GX_I2S_POWER_CONTROL(handle, 1u, false);
    (void)OPEN_CFW_GX_I2S_DISABLE(handle);
    (void)OPEN_CFW_GX_I2S_DEINITIALIZE(handle);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 10
__attribute__((used, noinline))
void open_cfw_gx8002_i2s_rx_buffer_get(void **buffer_out,
    uint32_t *length_out)
{
    struct {
        uintptr_t address;
        uint32_t length;
    } descriptor = {0u, 3200u};

    descriptor.address =
        (uintptr_t)OPEN_CFW_GX_I2S_DMA_GET_BUFFER(OPEN_CFW_GX_I2S_HANDLE, 0u);
    (void)OPEN_CFW_GX_CACHE_INVALIDATE(&descriptor, 0u);
    *buffer_out = (void *)descriptor.address;
    *length_out = descriptor.length;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 11
__attribute__((used, noinline))
void open_cfw_gx8002_audio_thread_notify(void)
{
    OPEN_CFW_GX_AUDIO_NOTIFY();
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 12
__attribute__((used, noinline))
void open_cfw_gx8002_reboot(bool skip_boot_wait)
{
    OPEN_CFW_GX_POWER_OFF();
    (void)OPEN_CFW_GX_DELAY(100u);
    OPEN_CFW_GX_POWER_ON();
    if (!skip_boot_wait) {
        (void)OPEN_CFW_GX_DELAY(1500u);
    }
}
#endif
