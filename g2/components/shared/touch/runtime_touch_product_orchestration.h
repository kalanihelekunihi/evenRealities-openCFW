/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_PRODUCT_ORCHESTRATION_H
#define OPEN_CFW_RUNTIME_TOUCH_PRODUCT_ORCHESTRATION_H

#include <stdint.h>

typedef struct open_cfw_touch_product_state {
    uint8_t mode;
    uint32_t countdown;
} open_cfw_touch_product_state;

typedef struct open_cfw_touch_product_provider {
    uint32_t (*startup)(void *context);
    void (*install_callback)(void *context, uint32_t argument);
    void (*fault)(void *context, uint32_t reason);
    void (*log_event)(void *context, uint32_t event);
    void (*enable_interrupts)(void *context);
    void (*bootstrap_storage)(void *context);
    void (*sample_configuration)(void *context);
    void (*start_power_callback)(void *context);
    void (*initialize_sensing)(void *context);
    uint32_t (*start_application)(void *context);
    void (*prepare_application)(void *context);
    void (*announce_application)(void *context);
    void (*sleep)(void *context);
    void (*refresh)(void *context);
    uint32_t (*tick)(void *context);
    void (*delay_until)(void *context, uint32_t tick);
    uint32_t (*pending)(void *context);
    void (*wait_primary)(void *context);
    void (*wait_secondary)(void *context);
    uint32_t (*process_objects)(void *context);
    uint32_t (*decision)(void *context, uint32_t selector);
    void (*idle)(void *context);
    void (*prepare_mode_three)(void *context);
    uint32_t (*mode_three_result)(void *context);
    void *context;
} open_cfw_touch_product_provider;

typedef struct open_cfw_touch_bringup_provider {
    uint32_t (*initialize_configuration)(void *context);
    void (*resolve_interrupt)(void *context, int16_t *interrupt_number);
    uint32_t (*run_application)(void *context);
    void *context;
} open_cfw_touch_bringup_provider;

uint32_t open_cfw_touch_product_05e0_bringup(
    const open_cfw_touch_bringup_provider *provider,
    volatile uint32_t *enable_register,
    volatile uint32_t *pending_register);
uint32_t open_cfw_touch_product_09b4_initialize(
    open_cfw_touch_product_state *state,
    volatile uint32_t *setup_control,
    const open_cfw_touch_product_provider *provider);
void open_cfw_touch_product_09b4_step(
    open_cfw_touch_product_state *state, uint8_t scratch[16],
    const open_cfw_touch_product_provider *provider);
void open_cfw_touch_product_09b4_run(
    open_cfw_touch_product_state *state, uint8_t scratch[16],
    volatile uint32_t *setup_control,
    const open_cfw_touch_product_provider *provider);

#endif
