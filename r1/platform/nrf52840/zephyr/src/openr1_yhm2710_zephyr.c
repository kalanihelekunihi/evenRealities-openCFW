#include "openr1_yhm2710_zephyr.h"

#include <errno.h>
#include <stddef.h>

#include <hal/nrf_gpio.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1/r1_power_lease.h"
#include "openr1_analog_zephyr.h"
#include "openr1_touch_zephyr.h"
#include "yhm2710/yhm2710.h"

#define OPENR1_POWER_NODE DT_NODELABEL(openr1_power)
#define OPENR1_YHM2710_PIN NRF_GPIO_PIN_MAP(1, 1)
#define OPENR1_NRF52840_CORE_MHZ 64u

typedef struct {
    int (*initialize)(void);
    bool (*provider_available)(void);
    bool (*optical_acquire)(void);
    bool (*optical_release)(void);
    uint8_t (*active_clients)(void);
    int (*last_error)(void);
} openr1_yhm2710_zephyr_api;

static const struct gpio_dt_spec stacmd_gpio =
    GPIO_DT_SPEC_GET(OPENR1_POWER_NODE, pmic_stacmd_gpios);

K_MUTEX_DEFINE(shared_power_mutex);

static struct k_work_delayable touch_release_work;
static yhm2710_stacmd_device stacmd;
static yhm2710_device pmic;
static r1_power_lease power_lease;
static atomic_t last_error;
static bool provider_ready;
static bool module_initialized;

static void record_error(int error) {
    if (error != 0) {
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static void drive_low(uint32_t pin) {
    if (pin == OPENR1_YHM2710_PIN) {
        nrf_gpio_pin_clear(pin);
    }
}

static void release_high(uint32_t pin) {
    if (pin == OPENR1_YHM2710_PIN) {
        nrf_gpio_pin_set(pin);
    }
}

static void set_output(uint32_t pin) {
    if (pin == OPENR1_YHM2710_PIN) {
        nrf_gpio_cfg_output(pin);
    }
}

static void set_input(uint32_t pin, uint32_t pull) {
    if (pin == OPENR1_YHM2710_PIN && pull <= NRF_GPIO_PIN_PULLUP) {
        nrf_gpio_cfg_input(pin, (nrf_gpio_pin_pull_t)pull);
    }
}

static uint32_t read_pin(uint32_t pin) {
    return pin == OPENR1_YHM2710_PIN ? nrf_gpio_pin_read(pin) : 0u;
}

static void delay_microseconds(uint32_t microseconds) {
    k_busy_wait(microseconds);
}

static void delay_core_cycles(uint32_t cycles) {
    const uint32_t microseconds =
        (cycles + OPENR1_NRF52840_CORE_MHZ - 1u) /
        OPENR1_NRF52840_CORE_MHZ;
    k_busy_wait(microseconds);
}

static bool set_shared_power_enabled(void *context, bool enabled) {
    (void)context;
    return provider_ready && yhm2710_set_shared_power_enabled(&pmic, enabled);
}

static const r1_power_provider_ops power_provider = {
    set_shared_power_enabled,
};

static bool acquire_client(r1_power_client client) {
    if (!provider_ready || k_is_in_isr()) {
        return false;
    }
    if (client == R1_POWER_CLIENT_TOUCH) {
        (void)k_work_cancel_delayable(&touch_release_work);
    }
    if (k_mutex_lock(&shared_power_mutex, K_FOREVER) != 0) {
        return false;
    }
    const r1_error error = r1_power_lease_acquire(&power_lease, client);
    (void)k_mutex_unlock(&shared_power_mutex);
    if (error != R1_OK) {
        record_error(-EIO);
    }
    return error == R1_OK;
}

static bool release_client(r1_power_client client) {
    if (!provider_ready || k_is_in_isr()) {
        return false;
    }
    if (k_mutex_lock(&shared_power_mutex, K_FOREVER) != 0) {
        return false;
    }
    const r1_error error = r1_power_lease_release(&power_lease, client);
    (void)k_mutex_unlock(&shared_power_mutex);
    if (error != R1_OK) {
        record_error(-EIO);
    }
    return error == R1_OK;
}

static void delayed_touch_release(struct k_work *work) {
    (void)work;
    (void)release_client(R1_POWER_CLIENT_TOUCH);
}

static bool analog_acquire(void *context) {
    (void)context;
    return acquire_client(R1_POWER_CLIENT_BATTERY_SAMPLING);
}

static void analog_release(void *context) {
    (void)context;
    (void)release_client(R1_POWER_CLIENT_BATTERY_SAMPLING);
}

static bool touch_acquire(void *context, uint8_t client_bit) {
    (void)context;
    return client_bit == (uint8_t)R1_POWER_CLIENT_TOUCH &&
           acquire_client(R1_POWER_CLIENT_TOUCH);
}

static bool touch_release_after(void *context, uint8_t client_bit,
                                uint32_t delay_ticks) {
    (void)context;
    if (client_bit != (uint8_t)R1_POWER_CLIENT_TOUCH || !provider_ready ||
        k_is_in_isr()) {
        return false;
    }
    if (delay_ticks == 0u) {
        (void)k_work_cancel_delayable(&touch_release_work);
        return release_client(R1_POWER_CLIENT_TOUCH);
    }
    return k_work_reschedule(&touch_release_work, K_TICKS(delay_ticks)) >= 0;
}

int openr1_yhm2710_zephyr_initialize(void) {
    static const openr1_analog_zephyr_power_ops analog_operations = {
        analog_acquire, analog_release,
    };
    static const openr1_touch_zephyr_power_ops touch_operations = {
        touch_acquire, touch_release_after,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    if (!gpio_is_ready_dt(&stacmd_gpio)) {
        return -ENODEV;
    }
    module_initialized = true;
    provider_ready = false;
    atomic_clear(&last_error);
    k_work_init_delayable(&touch_release_work, delayed_touch_release);
    r1_power_lease_initialize(&power_lease);

    const yhm2710_stacmd_line line = {
        .pin = OPENR1_YHM2710_PIN,
        .drive_low = drive_low,
        .release_high = release_high,
        .set_output = set_output,
        .set_input = set_input,
        .input_pull = NRF_GPIO_PIN_PULLUP,
        .read_pin = read_pin,
        .delay_cycles = delay_microseconds,
    };
    const yhm2710_bindings bindings = {
        .delay_cycles = delay_core_cycles,
    };
    nrf_gpio_cfg_input(OPENR1_YHM2710_PIN, NRF_GPIO_PIN_PULLUP);
    yhm2710_stacmd_initialize(&stacmd, &line);
    (void)yhm2710_stacmd_open(&stacmd);
    yhm2710_initialize_with_stacmd(&pmic, &stacmd, &bindings);
    if (yhm2710_configure(&pmic) != 0u) {
        record_error(-ENODEV);
        (void)yhm2710_stacmd_close(&stacmd);
        nrf_gpio_cfg_input(OPENR1_YHM2710_PIN, NRF_GPIO_PIN_PULLUP);
        return 0;
    }
    if (r1_power_lease_bind(&power_lease, &power_provider, NULL) != R1_OK) {
        record_error(-EIO);
        return -EIO;
    }
    provider_ready = true;
    int error = openr1_analog_zephyr_bind_power(&analog_operations, NULL);
    if (error == 0) {
        error = openr1_touch_zephyr_bind_power(&touch_operations, NULL);
    }
    if (error != 0) {
        provider_ready = false;
        record_error(error);
    }
    return error;
}

bool openr1_yhm2710_zephyr_provider_available(void) {
    return provider_ready;
}

bool openr1_yhm2710_zephyr_optical_acquire(void) {
    return acquire_client(R1_POWER_CLIENT_OPTICAL_PPG);
}

bool openr1_yhm2710_zephyr_optical_release(void) {
    return release_client(R1_POWER_CLIENT_OPTICAL_PPG);
}

uint8_t openr1_yhm2710_zephyr_active_clients(void) {
    return r1_power_lease_active_mask(&power_lease);
}

int openr1_yhm2710_zephyr_last_error(void) {
    return (int)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_yhm2710_zephyr_api yhm2710_zephyr_api = {
    openr1_yhm2710_zephyr_initialize,
    openr1_yhm2710_zephyr_provider_available,
    openr1_yhm2710_zephyr_optical_acquire,
    openr1_yhm2710_zephyr_optical_release,
    openr1_yhm2710_zephyr_active_clients,
    openr1_yhm2710_zephyr_last_error,
};
