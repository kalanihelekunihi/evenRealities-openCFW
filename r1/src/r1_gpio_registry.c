#include "openr1/r1_gpio_registry.h"

static bool r1_gpio_name_equal(const char *left, const char *right) {
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

size_t r1_gpio_input_irq_dispatch(
    const r1_gpio_input_irq_record records[R1_GPIO_INPUT_REGISTRY_COUNT],
    uint32_t linear_pin,
    uint32_t action) {
    size_t dispatched = 0u;

    if (records == NULL) {
        return 0u;
    }
    for (size_t index = 0u; index < R1_GPIO_INPUT_REGISTRY_COUNT; ++index) {
        if (records[index].linear_pin == linear_pin &&
            records[index].callback != NULL) {
            records[index].callback((uint8_t)linear_pin, action);
            ++dispatched;
        }
    }
    return dispatched;
}

r1_gpio_input_open_plan r1_gpio_input_open_plan_build(
    const r1_gpio_input_open_record
        records[R1_GPIO_INPUT_REGISTRY_COUNT],
    const char *requested_name,
    bool gpiote_initialized) {
    r1_gpio_input_open_plan plan = {.provider_status = UINT8_C(2)};
    if (records == NULL || requested_name == NULL) {
        return plan;
    }
    for (size_t index = 0u; index < R1_GPIO_INPUT_REGISTRY_COUNT; ++index) {
        if (records[index].name == NULL ||
            !r1_gpio_name_equal(records[index].name, requested_name)) {
            continue;
        }
        plan.provider_status = 0u;
        plan.record_index = (uint8_t)index;
        if (records[index].open) {
            return plan;
        }
        plan.linear_pin = records[index].linear_pin;
        plan.pin_cnf_raw = UINT32_C(2);
        plan.pull_raw = records[index].pull_raw;
        plan.polarity_raw = records[index].polarity_raw;
        plan.initialize_gpiote = !gpiote_initialized;
        plan.configure_port_event = true;
        plan.enable_event = true;
        plan.mark_open = true;
        return plan;
    }
    return plan;
}
