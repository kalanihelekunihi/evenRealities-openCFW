#include "openr1_touch_zephyr.h"

#include <errno.h>
#include <stddef.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#define OPENR1_TOUCH_NODE DT_NODELABEL(openr1_touch)
#define OPENR1_TOUCH_BUS_NODE DT_PHANDLE(OPENR1_TOUCH_NODE, touch_bus)

#define OPENR1_TOUCH_FLAG_IRQ BIT(0)
#define OPENR1_TOUCH_FLAG_OPEN BIT(1)
#define OPENR1_TOUCH_FLAG_CLOSE BIT(2)
#define OPENR1_TOUCH_FLAG_RESTART BIT(3)
#define OPENR1_TOUCH_FLAGS \
    (OPENR1_TOUCH_FLAG_IRQ | OPENR1_TOUCH_FLAG_OPEN | \
     OPENR1_TOUCH_FLAG_CLOSE | OPENR1_TOUCH_FLAG_RESTART)

typedef struct {
    int (*initialize)(void);
    int (*bind_power)(const openr1_touch_zephyr_power_ops *, void *);
    int (*set_identity)(r1_iqs7211e_layout, uint8_t);
    int (*acquire)(uint8_t);
    int (*release)(uint8_t);
    int (*set_enabled)(bool);
    void (*set_sample_callback)(r1_iqs7211e_sample_callback, void *);
    bool (*is_provisioned)(void);
    bool (*is_active)(void);
    uint32_t (*last_error)(void);
} openr1_touch_zephyr_api;

static const struct device *const touch_bus =
    DEVICE_DT_GET(OPENR1_TOUCH_BUS_NODE);
static const struct gpio_dt_spec touch_ldo =
    GPIO_DT_SPEC_GET(OPENR1_TOUCH_NODE, touch_ldo_gpios);
static const struct gpio_dt_spec touch_rdy =
    GPIO_DT_SPEC_GET(OPENR1_TOUCH_NODE, touch_rdy_gpios);

K_MUTEX_DEFINE(touch_bus_mutex);
K_MUTEX_DEFINE(touch_state_mutex);
K_EVENT_DEFINE(touch_events);

static struct gpio_callback touch_rdy_callback;
static struct k_timer touch_restart_timer;
static r1_iqs7211e_adapter touch_adapter;
static const openr1_touch_zephyr_power_ops *power_ops;
static void *power_context;
static atomic_t source_mask;
static atomic_t last_error;
static atomic_t identity_valid;
static atomic_t hardware_active;
static atomic_t touch_enabled;
static bool callback_registered;
static bool rdy_input_configured;
static bool module_initialized;

static void record_r1_error(r1_error error) {
    if (error != R1_OK) {
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static bool power_provider_complete(void) {
    bool complete = false;
    if (k_mutex_lock(&touch_state_mutex, K_FOREVER) == 0) {
        complete = power_ops != NULL && power_ops->acquire != NULL &&
                   power_ops->release_after != NULL;
        (void)k_mutex_unlock(&touch_state_mutex);
    }
    return complete;
}

static int32_t provider_read(void *context, uint8_t device_address,
                             uint8_t register_address, uint8_t *bytes,
                             size_t length) {
    (void)context;
    if (!module_initialized || device_address != R1_IQS7211E_ADDRESS ||
        bytes == NULL || length == 0u) {
        return -1;
    }
    if (k_mutex_lock(&touch_bus_mutex, K_FOREVER) != 0) {
        return -1;
    }
    const int error = i2c_write_read(
        touch_bus, device_address, &register_address, 1u, bytes, length);
    (void)k_mutex_unlock(&touch_bus_mutex);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    return 0;
}

static int32_t provider_write(void *context, uint8_t device_address,
                              uint8_t register_address, const uint8_t *bytes,
                              size_t length) {
    (void)context;
    if (!module_initialized || device_address != R1_IQS7211E_ADDRESS ||
        length > R1_IQS7211E_CONFIG_MAX_WRITE ||
        (length != 0u && bytes == NULL)) {
        return -1;
    }
    uint8_t frame[R1_IQS7211E_CONFIG_MAX_WRITE + 1u];
    frame[0] = register_address;
    if (length != 0u) {
        memcpy(frame + 1u, bytes, length);
    }
    if (k_mutex_lock(&touch_bus_mutex, K_FOREVER) != 0) {
        return -1;
    }
    const int error = i2c_write(
        touch_bus, frame, length + 1u, device_address);
    (void)k_mutex_unlock(&touch_bus_mutex);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    return 0;
}

static void touch_rdy_interrupt(const struct device *port,
                                struct gpio_callback *callback,
                                gpio_port_pins_t pins) {
    (void)port;
    (void)callback;
    (void)pins;
    (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_IRQ);
}

static void rdy_input_close(void) {
    if (rdy_input_configured) {
        (void)gpio_pin_interrupt_configure_dt(
            &touch_rdy, GPIO_INT_DISABLE);
        rdy_input_configured = false;
    }
}

static bool rdy_input_open(void) {
    int error = gpio_pin_configure_dt(&touch_rdy, GPIO_INPUT);
    if (error != 0) {
        atomic_set(&last_error, error);
        return false;
    }
    if (!callback_registered) {
        gpio_init_callback(&touch_rdy_callback, touch_rdy_interrupt,
                           BIT(touch_rdy.pin));
        error = gpio_add_callback(touch_rdy.port, &touch_rdy_callback);
        if (error != 0) {
            atomic_set(&last_error, error);
            return false;
        }
        callback_registered = true;
    }
    error = gpio_pin_interrupt_configure_dt(
        &touch_rdy, GPIO_INT_EDGE_TO_INACTIVE);
    if (error != 0) {
        atomic_set(&last_error, error);
        return false;
    }
    rdy_input_configured = true;
    return true;
}

static void board_power_down(void) {
    atomic_clear(&hardware_active);
    rdy_input_close();
    (void)gpio_pin_configure_dt(&touch_ldo, GPIO_OUTPUT_INACTIVE);
    (void)gpio_pin_configure_dt(&touch_rdy, GPIO_OUTPUT_INACTIVE);
}

static bool board_open(void *context) {
    (void)context;
    const openr1_touch_zephyr_power_ops *operations = NULL;
    void *operations_context = NULL;
    if (k_mutex_lock(&touch_state_mutex, K_FOREVER) == 0) {
        operations = power_ops;
        operations_context = power_context;
        (void)k_mutex_unlock(&touch_state_mutex);
    }
    if (operations == NULL || operations->acquire == NULL ||
        operations->release_after == NULL ||
        !operations->acquire(
            operations_context, OPENR1_TOUCH_ZEPHYR_POWER_CLIENT_BIT)) {
        board_power_down();
        return false;
    }
    if (!operations->release_after(
            operations_context, OPENR1_TOUCH_ZEPHYR_POWER_CLIENT_BIT,
            OPENR1_TOUCH_ZEPHYR_POWER_RELEASE_TICKS)) {
        (void)operations->release_after(
            operations_context, OPENR1_TOUCH_ZEPHYR_POWER_CLIENT_BIT, 0u);
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(1));
    if (gpio_pin_configure_dt(&touch_ldo, GPIO_OUTPUT_ACTIVE) != 0) {
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(10));
    rdy_input_close();
    if (gpio_pin_configure_dt(&touch_rdy, GPIO_OUTPUT_ACTIVE) != 0 ||
        gpio_pin_set_dt(&touch_rdy, 0) != 0) {
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(130));
    if (gpio_pin_set_dt(&touch_rdy, 1) != 0) {
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(10));
    if (gpio_pin_configure_dt(&touch_rdy, GPIO_DISCONNECTED) != 0) {
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(20));
    if (!rdy_input_open()) {
        board_power_down();
        return false;
    }
    k_sleep(K_TICKS(20));
    atomic_set(&hardware_active, 1);
    return true;
}

static void board_close(void *context) {
    (void)context;
    board_power_down();
}

static void restart_timer_callback(struct k_timer *timer) {
    (void)timer;
    (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_RESTART);
}

static bool board_schedule_open(void *context, uint32_t delay_ticks) {
    (void)context;
    k_timer_start(&touch_restart_timer, K_TICKS(delay_ticks), K_NO_WAIT);
    return true;
}

static bool source_requested(void) {
    return atomic_get(&touch_enabled) != 0 &&
           atomic_get(&source_mask) != 0;
}

static void process_close(void) {
    if (source_requested()) {
        return;
    }
    k_timer_stop(&touch_restart_timer);
    if (touch_adapter.configured) {
        record_r1_error(r1_iqs7211e_deactivate(&touch_adapter));
    } else {
        board_power_down();
        touch_adapter.configured = false;
        touch_adapter.restart_pending = false;
    }
}

static void process_open(void) {
    if (!source_requested() || atomic_get(&identity_valid) == 0 ||
        atomic_get(&hardware_active) != 0 || !power_provider_complete()) {
        return;
    }
    record_r1_error(r1_iqs7211e_configure(
        &touch_adapter, touch_adapter.layout, touch_adapter.ring_size));
}

static void process_restart(void) {
    if (!source_requested() || atomic_get(&identity_valid) == 0 ||
        !touch_adapter.restart_pending) {
        return;
    }
    record_r1_error(r1_iqs7211e_resume_scheduled_restart(&touch_adapter));
}

static void process_irq(void) {
    if (!source_requested() || atomic_get(&hardware_active) == 0 ||
        gpio_pin_get_dt(&touch_rdy) != 0) {
        return;
    }
    const uint8_t factory_marker =
        ((uint32_t)atomic_get(&source_mask) &
         (UINT32_C(1) << OPENR1_TOUCH_ZEPHYR_SOURCE_FACTORY)) != 0u
            ? UINT8_C(0x55) : 0u;
    record_r1_error(r1_iqs7211e_process_irq(
        &touch_adapter, factory_marker));
}

static void touch_worker(void *first, void *second, void *third) {
    (void)first;
    (void)second;
    (void)third;
    for (;;) {
        const uint32_t flags = k_event_wait(
            &touch_events, OPENR1_TOUCH_FLAGS, true, K_FOREVER);
        if ((flags & OPENR1_TOUCH_FLAG_CLOSE) != 0u) {
            process_close();
        }
        if ((flags & OPENR1_TOUCH_FLAG_OPEN) != 0u) {
            process_open();
        }
        if ((flags & OPENR1_TOUCH_FLAG_RESTART) != 0u) {
            process_restart();
        }
        if ((flags & OPENR1_TOUCH_FLAG_IRQ) != 0u) {
            process_irq();
        }
    }
}

K_THREAD_DEFINE(openr1_touch_thread, 2048, touch_worker,
                NULL, NULL, NULL, K_LOWEST_APPLICATION_THREAD_PRIO, 0, 0);

int openr1_touch_zephyr_initialize(void) {
    static const r1_iqs7211e_provider_ops provider = {
        provider_read, provider_write,
    };
    static const r1_iqs7211e_board_ops board = {
        board_open, board_close, board_schedule_open,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    if (!device_is_ready(touch_bus) || !gpio_is_ready_dt(&touch_ldo) ||
        !gpio_is_ready_dt(&touch_rdy)) {
        return -ENODEV;
    }
    atomic_clear(&source_mask);
    atomic_clear(&last_error);
    atomic_clear(&identity_valid);
    atomic_clear(&hardware_active);
    atomic_set(&touch_enabled, 1);
    callback_registered = false;
    rdy_input_configured = false;
    k_timer_init(&touch_restart_timer, restart_timer_callback, NULL);
    board_power_down();
    r1_iqs7211e_adapter_initialize(&touch_adapter);
    if (r1_iqs7211e_adapter_bind(
            &touch_adapter, &provider, NULL, &board, NULL) != R1_OK) {
        return -EIO;
    }
    module_initialized = true;
    return 0;
}

int openr1_touch_zephyr_bind_power(
    const openr1_touch_zephyr_power_ops *operations, void *context) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (operations == NULL || operations->acquire == NULL ||
        operations->release_after == NULL) {
        return -EINVAL;
    }
    if (k_mutex_lock(&touch_state_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    const bool busy = atomic_get(&hardware_active) != 0 ||
                      touch_adapter.configured ||
                      touch_adapter.restart_pending;
    if (!busy) {
        power_ops = operations;
        power_context = context;
    }
    (void)k_mutex_unlock(&touch_state_mutex);
    if (busy) {
        return -EBUSY;
    }
    if (atomic_get(&identity_valid) != 0 && source_requested()) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_OPEN);
    }
    return 0;
}

int openr1_touch_zephyr_set_identity(r1_iqs7211e_layout layout,
                                     uint8_t ring_size) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (r1_iqs7211e_calibration_for(layout, ring_size) == NULL) {
        return -EINVAL;
    }
    if (k_mutex_lock(&touch_state_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    const bool busy = atomic_get(&hardware_active) != 0 ||
                      touch_adapter.configured ||
                      touch_adapter.restart_pending;
    if (!busy) {
        touch_adapter.layout = layout;
        touch_adapter.ring_size = ring_size;
        atomic_set(&identity_valid, 1);
    }
    (void)k_mutex_unlock(&touch_state_mutex);
    if (busy) {
        return -EBUSY;
    }
    if (power_provider_complete() && source_requested()) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_OPEN);
    }
    return 0;
}

int openr1_touch_zephyr_acquire(uint8_t source) {
    if (!module_initialized || source >= 32u) {
        return -EINVAL;
    }
    const atomic_val_t bit = (atomic_val_t)(UINT32_C(1) << source);
    const atomic_val_t previous = atomic_or(&source_mask, bit);
    if (previous == 0 && atomic_get(&touch_enabled) != 0 &&
        atomic_get(&identity_valid) != 0 && power_provider_complete()) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_OPEN);
    }
    return 0;
}

int openr1_touch_zephyr_release(uint8_t source) {
    if (!module_initialized || source >= 32u) {
        return -EINVAL;
    }
    const atomic_val_t bit = (atomic_val_t)(UINT32_C(1) << source);
    const atomic_val_t previous = atomic_and(&source_mask, ~bit);
    if (previous != 0 && atomic_get(&source_mask) == 0) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_CLOSE);
    }
    return 0;
}

int openr1_touch_zephyr_set_enabled(bool enabled) {
    if (!module_initialized) {
        return -EACCES;
    }
    const atomic_val_t previous = atomic_set(
        &touch_enabled, enabled ? 1 : 0);
    const bool requested = atomic_get(&source_mask) != 0;
    if ((previous != 0) == enabled || !requested) {
        return 0;
    }
    if (!enabled) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_CLOSE);
    } else if (atomic_get(&identity_valid) != 0 &&
               power_provider_complete()) {
        (void)k_event_post(&touch_events, OPENR1_TOUCH_FLAG_OPEN);
    }
    return 0;
}

void openr1_touch_zephyr_set_sample_callback(
    r1_iqs7211e_sample_callback callback, void *context) {
    r1_iqs7211e_set_sample_callback(&touch_adapter, callback, context);
}

bool openr1_touch_zephyr_is_provisioned(void) {
    return module_initialized && atomic_get(&identity_valid) != 0 &&
           power_provider_complete();
}

bool openr1_touch_zephyr_is_active(void) {
    return atomic_get(&hardware_active) != 0;
}

uint32_t openr1_touch_zephyr_last_error(void) {
    return (uint32_t)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_touch_zephyr_api touch_zephyr_api = {
    openr1_touch_zephyr_initialize,
    openr1_touch_zephyr_bind_power,
    openr1_touch_zephyr_set_identity,
    openr1_touch_zephyr_acquire,
    openr1_touch_zephyr_release,
    openr1_touch_zephyr_set_enabled,
    openr1_touch_zephyr_set_sample_callback,
    openr1_touch_zephyr_is_provisioned,
    openr1_touch_zephyr_is_active,
    openr1_touch_zephyr_last_error,
};
