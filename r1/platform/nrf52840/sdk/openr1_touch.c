#include "openr1_touch.h"

#include <stddef.h>
#include <string.h>

#include "cmsis_os2.h"
#include "FreeRTOS.h"
#include "nrf_gpio.h"
#include "nrfx_gpiote.h"
#include "nrfx_twim.h"
#include "task.h"

#define OPENR1_TOUCH_TWIM_SCL_PIN 12u
#define OPENR1_TOUCH_TWIM_SDA_PIN 1u
#define OPENR1_TOUCH_LDO_ENABLE_PIN 30u
#define OPENR1_TOUCH_RDY_MCLR_PIN 17u
#define OPENR1_TOUCH_TWIM_PRIORITY 2u

#define OPENR1_TOUCH_FLAG_IRQ UINT32_C(0x01)
#define OPENR1_TOUCH_FLAG_OPEN UINT32_C(0x02)
#define OPENR1_TOUCH_FLAG_CLOSE UINT32_C(0x04)
#define OPENR1_TOUCH_FLAG_RESTART UINT32_C(0x08)
#define OPENR1_TOUCH_FLAGS (OPENR1_TOUCH_FLAG_IRQ | OPENR1_TOUCH_FLAG_OPEN | \
                            OPENR1_TOUCH_FLAG_CLOSE | OPENR1_TOUCH_FLAG_RESTART)

#ifndef OPENR1_TOUCH_LAYOUT
#define OPENR1_TOUCH_LAYOUT UINT8_MAX
#endif

#ifndef OPENR1_TOUCH_RING_SIZE
#define OPENR1_TOUCH_RING_SIZE 0u
#endif

static const nrfx_twim_t touch_twim = NRFX_TWIM_INSTANCE(0);
static r1_iqs7211e_adapter touch_adapter;

typedef bool (*openr1_ati_audit_begin_fn)(
    r1_iqs7211e_ati_audit_state, uint32_t, r1_iqs7211e_layout,
    r1_iqs7211e_ati_audit_request *);
typedef bool (*openr1_ati_audit_summarize_fn)(
    const uint16_t *, size_t, const uint8_t *,
    r1_iqs7211e_ati_audit_summary *);

__attribute__((used, section(".openr1_touch_audit_api")))
static const openr1_ati_audit_begin_fn retained_ati_audit_begin =
    r1_iqs7211e_ati_audit_begin;
__attribute__((used, section(".openr1_touch_audit_api")))
static const openr1_ati_audit_summarize_fn retained_ati_audit_summarize =
    r1_iqs7211e_ati_audit_summarize;
static osThreadId_t touch_thread;
static osTimerId_t restart_timer;
static StaticTask_t touch_control_block;
static StackType_t touch_stack[configMINIMAL_STACK_SIZE];
static const openr1_touch_power_ops *power_ops;
static void *power_context;
static volatile uint32_t source_mask;
static volatile uint32_t last_error;
static bool identity_valid;
static bool hardware_active;
static bool twim_active;
static bool rdy_input_configured;
static bool touch_enabled;

static void record_r1_error(r1_error error) {
    if (error != R1_OK) {
        last_error = (uint32_t)error;
    }
}

static bool power_provider_complete(void) {
    return power_ops != NULL && power_ops->acquire != NULL &&
           power_ops->release_after != NULL;
}

static bool twim_start(void) {
    if (twim_active) {
        return true;
    }
    const nrfx_twim_config_t configuration = {
        .scl = OPENR1_TOUCH_TWIM_SCL_PIN,
        .sda = OPENR1_TOUCH_TWIM_SDA_PIN,
        .frequency = NRF_TWIM_FREQ_400K,
        .interrupt_priority = OPENR1_TOUCH_TWIM_PRIORITY,
        .hold_bus_uninit = false,
    };
    const nrfx_err_t error = nrfx_twim_init(
        &touch_twim, &configuration, NULL, NULL);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return false;
    }
    nrfx_twim_enable(&touch_twim);
    twim_active = true;
    return true;
}

static void twim_stop(void) {
    if (twim_active) {
        nrfx_twim_disable(&touch_twim);
        nrfx_twim_uninit(&touch_twim);
        twim_active = false;
    }
}

static int32_t provider_read(void *context, uint8_t device_address,
                             uint8_t register_address, uint8_t *bytes,
                             size_t length) {
    (void)context;
    if (!twim_active || device_address != R1_IQS7211E_ADDRESS ||
        bytes == NULL || length == 0u) {
        return -1;
    }
    uint8_t address = register_address;
    nrfx_err_t error = nrfx_twim_tx(
        &touch_twim, device_address, &address, sizeof address, true);
    if (error == NRFX_SUCCESS) {
        error = nrfx_twim_rx(&touch_twim, device_address, bytes, length);
    }
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return -1;
    }
    return 0;
}

static int32_t provider_write(void *context, uint8_t device_address,
                              uint8_t register_address, const uint8_t *bytes,
                              size_t length) {
    (void)context;
    if (!twim_active || device_address != R1_IQS7211E_ADDRESS ||
        length > R1_IQS7211E_CONFIG_MAX_WRITE ||
        (length != 0u && bytes == NULL)) {
        return -1;
    }
    uint8_t frame[R1_IQS7211E_CONFIG_MAX_WRITE + 1u];
    frame[0] = register_address;
    if (length != 0u) {
        memcpy(frame + 1u, bytes, length);
    }
    const nrfx_err_t error = nrfx_twim_tx(
        &touch_twim, device_address, frame, length + 1u, false);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return -1;
    }
    return 0;
}

static void rdy_interrupt(nrfx_gpiote_pin_t pin,
                          nrf_gpiote_polarity_t action) {
    (void)pin;
    (void)action;
    if (touch_thread != NULL) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_IRQ);
    }
}

static void rdy_input_close(void) {
    if (rdy_input_configured) {
        nrfx_gpiote_in_event_disable(OPENR1_TOUCH_RDY_MCLR_PIN);
        nrfx_gpiote_in_uninit(OPENR1_TOUCH_RDY_MCLR_PIN);
        rdy_input_configured = false;
    }
}

static bool rdy_input_open(void) {
    if (!nrfx_gpiote_is_init() && nrfx_gpiote_init() != NRFX_SUCCESS) {
        return false;
    }
    const nrfx_gpiote_in_config_t configuration =
        NRFX_GPIOTE_CONFIG_IN_SENSE_HITOLO(false);
    const nrfx_err_t error = nrfx_gpiote_in_init(
        OPENR1_TOUCH_RDY_MCLR_PIN, &configuration, rdy_interrupt);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return false;
    }
    rdy_input_configured = true;
    nrfx_gpiote_in_event_enable(OPENR1_TOUCH_RDY_MCLR_PIN, true);
    return true;
}

static void board_power_down(void) {
    hardware_active = false;
    rdy_input_close();
    nrf_gpio_pin_clear(OPENR1_TOUCH_LDO_ENABLE_PIN);
    nrf_gpio_cfg_output(OPENR1_TOUCH_LDO_ENABLE_PIN);
    nrf_gpio_pin_clear(OPENR1_TOUCH_RDY_MCLR_PIN);
    nrf_gpio_cfg_output(OPENR1_TOUCH_RDY_MCLR_PIN);
}

static bool board_open(void *context) {
    (void)context;
    if (!power_provider_complete()) {
        board_power_down();
        return false;
    }
    if (!power_ops->acquire(power_context, OPENR1_TOUCH_POWER_CLIENT_BIT)) {
        board_power_down();
        return false;
    }
    if (!power_ops->release_after(power_context, OPENR1_TOUCH_POWER_CLIENT_BIT,
                                  OPENR1_TOUCH_POWER_RELEASE_TICKS)) {
        (void)power_ops->release_after(
            power_context, OPENR1_TOUCH_POWER_CLIENT_BIT, 0u);
        board_power_down();
        return false;
    }
    (void)osDelay(1u);
    nrf_gpio_cfg_output(OPENR1_TOUCH_LDO_ENABLE_PIN);
    nrf_gpio_pin_set(OPENR1_TOUCH_LDO_ENABLE_PIN);
    (void)osDelay(10u);
    rdy_input_close();
    nrf_gpio_pin_set(OPENR1_TOUCH_RDY_MCLR_PIN);
    nrf_gpio_cfg_output(OPENR1_TOUCH_RDY_MCLR_PIN);
    nrf_gpio_pin_clear(OPENR1_TOUCH_RDY_MCLR_PIN);
    (void)osDelay(130u);
    nrf_gpio_pin_set(OPENR1_TOUCH_RDY_MCLR_PIN);
    (void)osDelay(10u);
    nrf_gpio_cfg_default(OPENR1_TOUCH_RDY_MCLR_PIN);
    (void)osDelay(20u);
    if (!rdy_input_open()) {
        board_power_down();
        return false;
    }
    (void)osDelay(20u);
    hardware_active = true;
    return true;
}

static void board_close(void *context) {
    (void)context;
    board_power_down();
}

static void restart_timer_callback(void *context) {
    (void)context;
    if (touch_thread != NULL) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_RESTART);
    }
}

static bool board_schedule_open(void *context, uint32_t delay_ticks) {
    (void)context;
    return restart_timer != NULL &&
           osTimerStart(restart_timer, delay_ticks) == osOK;
}

static bool source_requested(void) {
    return touch_enabled && source_mask != 0u;
}

static void process_close(void) {
    if (source_requested()) {
        return;
    }
    if (restart_timer != NULL) {
        (void)osTimerStop(restart_timer);
    }
    if (touch_adapter.configured && twim_start()) {
        record_r1_error(r1_iqs7211e_deactivate(&touch_adapter));
    } else {
        board_power_down();
        touch_adapter.configured = false;
        touch_adapter.restart_pending = false;
    }
    twim_stop();
}

static void process_open(void) {
    if (!source_requested() || !identity_valid || hardware_active ||
        !power_provider_complete() || !twim_start()) {
        return;
    }
    record_r1_error(r1_iqs7211e_configure(
        &touch_adapter, touch_adapter.layout, touch_adapter.ring_size));
    twim_stop();
}

static void process_restart(void) {
    if (!source_requested() || !identity_valid ||
        !touch_adapter.restart_pending || !twim_start()) {
        return;
    }
    record_r1_error(r1_iqs7211e_resume_scheduled_restart(&touch_adapter));
    twim_stop();
}

static void process_irq(void) {
    if (!source_requested() || !hardware_active ||
        nrf_gpio_pin_read(OPENR1_TOUCH_RDY_MCLR_PIN) != 0u || !twim_start()) {
        return;
    }
    const uint8_t factory_marker =
        (source_mask & (UINT32_C(1) << OPENR1_TOUCH_SOURCE_FACTORY)) != 0u
        ? UINT8_C(0x55) : 0u;
    record_r1_error(r1_iqs7211e_process_irq(
        &touch_adapter, factory_marker));
    twim_stop();
}

static void touch_worker(void *context) {
    (void)context;
    for (;;) {
        const uint32_t flags = osThreadFlagsWait(
            OPENR1_TOUCH_FLAGS, osFlagsWaitAny, osWaitForever);
        if ((flags & osFlagsError) != 0u) {
            last_error = flags;
            continue;
        }
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

ret_code_t openr1_touch_initialize(void) {
    static const r1_iqs7211e_provider_ops provider = {
        provider_read, provider_write,
    };
    static const r1_iqs7211e_board_ops board = {
        board_open, board_close, board_schedule_open,
    };
    static const osThreadAttr_t thread_attributes = {
        .name = "touch",
        .cb_mem = &touch_control_block,
        .cb_size = sizeof touch_control_block,
        .stack_mem = touch_stack,
        .stack_size = sizeof touch_stack,
    };
    if (touch_thread != NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    source_mask = 0u;
    last_error = NRF_SUCCESS;
    identity_valid = false;
    hardware_active = false;
    twim_active = false;
    rdy_input_configured = false;
    touch_enabled = true;
    board_power_down();
    r1_iqs7211e_adapter_initialize(&touch_adapter);
    if (r1_iqs7211e_adapter_bind(
            &touch_adapter, &provider, NULL, &board, NULL) != R1_OK) {
        return NRF_ERROR_INTERNAL;
    }
    restart_timer = osTimerNew(
        restart_timer_callback, osTimerOnce, NULL, NULL);
    touch_thread = osThreadNew(touch_worker, NULL, &thread_attributes);
    if (restart_timer == NULL || touch_thread == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    if (r1_iqs7211e_calibration_for(
            (r1_iqs7211e_layout)OPENR1_TOUCH_LAYOUT,
            (uint8_t)OPENR1_TOUCH_RING_SIZE) != NULL) {
        return openr1_touch_set_identity(
            (r1_iqs7211e_layout)OPENR1_TOUCH_LAYOUT,
            (uint8_t)OPENR1_TOUCH_RING_SIZE);
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_touch_bind_power(const openr1_touch_power_ops *operations,
                                   void *context) {
    if (touch_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (operations == NULL || operations->acquire == NULL ||
        operations->release_after == NULL) {
        return NRF_ERROR_INVALID_PARAM;
    }
    taskENTER_CRITICAL();
    const bool busy = hardware_active || touch_adapter.configured ||
                      touch_adapter.restart_pending;
    if (!busy) {
        power_ops = operations;
        power_context = context;
    }
    taskEXIT_CRITICAL();
    if (busy) {
        return NRF_ERROR_BUSY;
    }
    if (identity_valid && source_requested()) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_OPEN);
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_touch_set_identity(r1_iqs7211e_layout layout,
                                     uint8_t ring_size) {
    if (touch_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (r1_iqs7211e_calibration_for(layout, ring_size) == NULL) {
        return NRF_ERROR_INVALID_PARAM;
    }
    taskENTER_CRITICAL();
    const bool busy = hardware_active || touch_adapter.configured ||
                      touch_adapter.restart_pending;
    if (!busy) {
        touch_adapter.layout = layout;
        touch_adapter.ring_size = ring_size;
        identity_valid = true;
    }
    taskEXIT_CRITICAL();
    if (busy) {
        return NRF_ERROR_BUSY;
    }
    if (power_provider_complete() && source_requested()) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_OPEN);
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_touch_acquire(uint8_t source) {
    if (source >= 32u || touch_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    taskENTER_CRITICAL();
    const uint32_t previous = source_mask;
    source_mask |= UINT32_C(1) << source;
    taskEXIT_CRITICAL();
    if (previous == 0u && touch_enabled && identity_valid &&
        power_provider_complete()) {
        const uint32_t flags = osThreadFlagsSet(
            touch_thread, OPENR1_TOUCH_FLAG_OPEN);
        if ((flags & osFlagsError) != 0u) {
            return NRF_ERROR_NO_MEM;
        }
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_touch_release(uint8_t source) {
    if (source >= 32u || touch_thread == NULL) {
        return NRF_ERROR_INVALID_PARAM;
    }
    taskENTER_CRITICAL();
    const uint32_t previous = source_mask;
    source_mask &= ~(UINT32_C(1) << source);
    const uint32_t current = source_mask;
    taskEXIT_CRITICAL();
    if (previous != 0u && current == 0u) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_CLOSE);
    }
    return NRF_SUCCESS;
}

ret_code_t openr1_touch_set_enabled(bool enabled) {
    if (touch_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    taskENTER_CRITICAL();
    const bool previous = touch_enabled;
    touch_enabled = enabled;
    const bool requested = source_mask != 0u;
    taskEXIT_CRITICAL();
    if (previous == enabled || !requested) {
        return NRF_SUCCESS;
    }
    if (!enabled) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_CLOSE);
    } else if (identity_valid && power_provider_complete()) {
        (void)osThreadFlagsSet(touch_thread, OPENR1_TOUCH_FLAG_OPEN);
    }
    return NRF_SUCCESS;
}

bool openr1_touch_is_provisioned(void) {
    return identity_valid && power_provider_complete();
}

bool openr1_touch_is_active(void) {
    return hardware_active;
}

uint32_t openr1_touch_last_error(void) {
    return last_error;
}
