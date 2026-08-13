#include "openr1/r1_twi_sync.h"

#include "cmsis_os2.h"
#include "app_error.h"
#include "nrf_drv_twi.h"
#include "nrf_gpio.h"
#include "nrfx.h"
#include "nrfx_coredep.h"

static uint32_t openr1_kernel_state(void *context) {
    (void)context;
    return (uint32_t)osKernelGetState();
}

static uint32_t openr1_tick_frequency(void *context) {
    (void)context;
    return osKernelGetTickFreq();
}

static int32_t openr1_semaphore_acquire(
    void *context, void *semaphore, uint32_t ticks) {
    (void)context;
    return (int32_t)osSemaphoreAcquire((osSemaphoreId_t)semaphore, ticks);
}

static void openr1_semaphore_release(void *context, void *semaphore) {
    (void)context;
    (void)osSemaphoreRelease((osSemaphoreId_t)semaphore);
}

static void openr1_delay_us(void *context, uint32_t microseconds) {
    (void)context;
    nrfx_coredep_delay_us(microseconds);
}

const r1_twi_sync_ops openr1_nrf52840_twi_sync_ops = {
    .context = NULL,
    .kernel_state = openr1_kernel_state,
    .tick_frequency = openr1_tick_frequency,
    .semaphore_acquire = openr1_semaphore_acquire,
    .semaphore_release = openr1_semaphore_release,
    .delay_us = openr1_delay_us,
};

static uint32_t openr1_twi_transmit(
    void *context, void *bus, uint8_t address, const uint8_t *data,
    uint32_t length, bool no_stop) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    (void)context;
    return nrfx_twim_tx(
        &instance->u.twim, address, data, (size_t)length, no_stop);
}

static uint32_t openr1_twi_receive(
    void *context, void *bus, uint8_t address, uint8_t *data,
    uint32_t length) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    (void)context;
    return nrfx_twim_rx(
        &instance->u.twim, address, data, (size_t)length);
}

static void openr1_twi_fatal_error(void *context, uint32_t status) {
    (void)context;
    APP_ERROR_CHECK(status);
}

const r1_twi_transfer_ops openr1_nrf52840_twi_transfer_ops = {
    .context = NULL,
    .transmit = openr1_twi_transmit,
    .receive = openr1_twi_receive,
    .fatal_error = openr1_twi_fatal_error,
    .sync = &openr1_nrf52840_twi_sync_ops,
};

static void openr1_twi_event_handler(
    const nrf_drv_twi_evt_t *event, void *context) {
    r1_twi_sync_state *state = context;
    if (event != NULL && state != NULL) {
        (void)r1_twi_sync_complete(
            state, (uint8_t)event->type, &openr1_nrf52840_twi_sync_ops);
    }
}

static void openr1_twi_configure_pin(void *context, uint32_t pin) {
    (void)context;
    nrf_gpio_cfg(
        pin, NRF_GPIO_PIN_DIR_OUTPUT, NRF_GPIO_PIN_INPUT_DISCONNECT,
        NRF_GPIO_PIN_NOPULL, NRF_GPIO_PIN_S0S1, NRF_GPIO_PIN_NOSENSE);
}

static uint32_t openr1_twi_initialize(
    void *context, void *bus, const r1_twi_lifecycle_config *config,
    r1_twi_sync_state *transfer_state) {
    const nrf_drv_twi_config_t provider_config = {
        .scl = config->scl_pin,
        .sda = config->sda_pin,
        .frequency = (nrf_drv_twi_frequency_t)config->frequency,
        .interrupt_priority = config->interrupt_priority,
        .clear_bus_init = config->clear_bus_init,
        .hold_bus_uninit = config->hold_bus_uninit,
    };
    (void)context;
    return nrf_drv_twi_init(
        (const nrf_drv_twi_t *)bus, &provider_config,
        openr1_twi_event_handler, transfer_state);
}

static void openr1_twi_enable(void *context, void *bus) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    (void)context;
    nrfx_twim_enable(&instance->u.twim);
}

static void openr1_twi_disable(void *context, void *bus) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    (void)context;
    nrfx_twim_disable(&instance->u.twim);
}

static void openr1_twi_uninitialize(void *context, void *bus) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    (void)context;
    nrfx_twim_uninit(&instance->u.twim);
}

static void openr1_twi_power_cycle(void *context, void *bus) {
    const nrf_drv_twi_t *instance = (const nrf_drv_twi_t *)bus;
    volatile uint32_t *power = (volatile uint32_t *)(
        (uintptr_t)instance->u.twim.p_twim + UINT32_C(0x0ffc));
    (void)context;
    *power = 0u;
    *power = 1u;
}

const r1_twi_lifecycle_ops openr1_nrf52840_twi_lifecycle_ops = {
    .context = NULL,
    .configure_pin = openr1_twi_configure_pin,
    .initialize = openr1_twi_initialize,
    .enable = openr1_twi_enable,
    .disable = openr1_twi_disable,
    .uninitialize = openr1_twi_uninitialize,
    .power_cycle = openr1_twi_power_cycle,
};

static void openr1_twi_release_pin(void *context, uint32_t pin) {
    (void)context;
    nrf_gpio_cfg_default(pin);
}

const r1_twi_software_lifecycle_ops
openr1_nrf52840_twi_software_lifecycle_ops = {
    .context = NULL,
    .release_pin = openr1_twi_release_pin,
};

typedef struct {
    const r1_twi_sync_ops *ops;
    const r1_twi_transfer_ops *transfer_ops;
    const r1_twi_lifecycle_ops *lifecycle_ops;
    const r1_twi_software_lifecycle_ops *software_lifecycle_ops;
    r1_error (*complete)(r1_twi_sync_state *, uint8_t,
                         const r1_twi_sync_ops *);
    uint32_t (*wait)(r1_twi_sync_state *, uint32_t,
                     const r1_twi_sync_ops *);
    uint32_t (*primary_read)(r1_twi_sync_state *, void *, uint8_t, uint8_t,
                             uint8_t *, uint32_t, const r1_twi_transfer_ops *);
    uint32_t (*primary_write)(r1_twi_sync_state *, void *, uint8_t, uint8_t,
                              const uint8_t *, uint32_t,
                              const r1_twi_transfer_ops *);
    uint32_t (*secondary_read)(r1_twi_sync_state *, void *, uint8_t, uint8_t,
                               uint8_t *, uint32_t,
                               const r1_twi_transfer_ops *);
    uint32_t (*secondary_write)(r1_twi_sync_state *, void *, uint8_t, uint8_t,
                                const uint8_t *, uint32_t,
                                const r1_twi_transfer_ops *);
    uint32_t (*lifecycle_initialize)(
        r1_twi_lifecycle_state *, void *, const r1_twi_lifecycle_config *,
        const r1_twi_lifecycle_ops *);
    uint32_t (*primary_lifecycle_initialize)(
        r1_twi_lifecycle_state *, void *, uint32_t, uint32_t,
        const r1_twi_lifecycle_ops *);
    uint32_t (*secondary_lifecycle_initialize)(
        r1_twi_lifecycle_state *, void *, uint32_t, uint32_t,
        const r1_twi_lifecycle_ops *);
    uint32_t (*lifecycle_shutdown)(
        r1_twi_lifecycle_state *, void *, const r1_twi_lifecycle_ops *);
    uint32_t (*software_lifecycle_shutdown)(
        r1_twi_software_lifecycle_state *,
        const r1_twi_software_lifecycle_ops *);
} openr1_twi_sync_api;

__attribute__((used, section(".openr1_twi_sync_api")))
static const openr1_twi_sync_api retained_twi_sync_api = {
    &openr1_nrf52840_twi_sync_ops,
    &openr1_nrf52840_twi_transfer_ops,
    &openr1_nrf52840_twi_lifecycle_ops,
    &openr1_nrf52840_twi_software_lifecycle_ops,
    r1_twi_sync_complete,
    r1_twi_sync_wait,
    r1_twi_primary_register_read,
    r1_twi_primary_register_write,
    r1_twi_secondary_register_read,
    r1_twi_secondary_register_write,
    r1_twi_lifecycle_initialize,
    r1_twi_primary_lifecycle_initialize,
    r1_twi_secondary_lifecycle_initialize,
    r1_twi_lifecycle_shutdown,
    r1_twi_software_lifecycle_shutdown,
};
