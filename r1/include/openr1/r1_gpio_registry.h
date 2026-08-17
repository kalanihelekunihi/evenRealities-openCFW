#ifndef OPENR1_R1_GPIO_REGISTRY_H
#define OPENR1_R1_GPIO_REGISTRY_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#define R1_GPIO_INPUT_REGISTRY_COUNT 7u

typedef void (*r1_gpio_input_irq_callback)(uint8_t linear_pin,
                                           uint32_t action);

typedef struct {
    uint32_t linear_pin;
    r1_gpio_input_irq_callback callback;
} r1_gpio_input_irq_record;

typedef struct {
    const char *name;
    uint32_t linear_pin;
    uint8_t pull_raw;
    uint8_t polarity_raw;
    bool open;
} r1_gpio_input_open_record;

typedef struct {
    uint8_t provider_status;
    uint8_t record_index;
    uint32_t linear_pin;
    uint32_t pin_cnf_raw;
    uint8_t pull_raw;
    uint8_t polarity_raw;
    bool initialize_gpiote;
    bool configure_port_event;
    bool enable_event;
    bool mark_open;
} r1_gpio_input_open_plan;

/* Dispatches a provider-reported pin/action to every matching product record.
 * This performs no GPIO read, write, configuration, or interrupt operation. */
size_t r1_gpio_input_irq_dispatch(
    const r1_gpio_input_irq_record records[R1_GPIO_INPUT_REGISTRY_COUNT],
    uint32_t linear_pin,
    uint32_t action);

/* Builds the exact seven-record name/open/configuration decision without
 * touching GPIO or invoking Nordic GPIOTE. Status 0 is success (including an
 * already-open record); status 2 is name-not-found. */
r1_gpio_input_open_plan r1_gpio_input_open_plan_build(
    const r1_gpio_input_open_record
        records[R1_GPIO_INPUT_REGISTRY_COUNT],
    const char *requested_name,
    bool gpiote_initialized);

#endif
