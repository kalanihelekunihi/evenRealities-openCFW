/* Stock 50304/50338 and their four six-byte product wrappers.
 * Handles are owned/populated by native_peripheral_bindings.c. */
#include "../registry/stock_registry.h"
extern generic_device_registry_device *volatile r1_led_enable_device;
extern generic_device_registry_device *volatile r1_touch_ldo_device;

void r1_peripheral_line_release(uint32_t index) {
    generic_device_registry_device *volatile *cell;
    if (index == 0)
        cell = &r1_led_enable_device;
    else if (index == 1)
        cell = &r1_touch_ldo_device;
    else
        return;
    (void)r1_stock_dispatch_18(*cell, 0, 0);
    /* Stock reloads after the operation, including its callback effects. */
    (void)r1_stock_dispatch_0c(*cell);
}

void r1_peripheral_line_acquire(uint32_t index) {
    generic_device_registry_device *volatile *cell;
    if (index == 0)
        cell = &r1_led_enable_device;
    else if (index == 1)
        cell = &r1_touch_ldo_device;
    else
        return;
    (void)r1_stock_dispatch_08(*cell);
    (void)r1_stock_dispatch_18(*cell, 1, 0);
}

void r1_goodix_transport_release(void) { r1_peripheral_line_release(0); }
void r1_goodix_transport_prepare(void) { r1_peripheral_line_acquire(0); }
/* Historical touch labels in the frontier say enable_on/acquire_on; their
 * actual targets are the release/acquire helpers with selector one. */
void r1_touch_bus_enable_on(void) { r1_peripheral_line_release(1); }
void r1_touch_bus_acquire_on(void) { r1_peripheral_line_acquire(1); }
