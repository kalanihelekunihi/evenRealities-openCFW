#ifndef R1_NAMED_GPIO_H
#define R1_NAMED_GPIO_H
#include "../registry/stock_registry.h"
typedef struct {
    const char *name;
    uint8_t opened, reserved_05[3];
    uint32_t pin;
    uint8_t pull, polarity, reserved_0e[2];
    generic_device_registry_device device;
    uintptr_t callback;
} r1_named_gpio_record;
extern r1_named_gpio_record r1_named_gpio_records[7];
uint32_t r1_named_gpio_register_all(void);
uint32_t r1_named_gpio_callback(generic_device_registry_device *device,uintptr_t operation,uintptr_t callback);
uint32_t r1_named_gpio_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t output,uintptr_t extra);
uint32_t r1_named_gpio_close(generic_device_registry_device *device);
/* Native original 0x54B90 event-open body. */
uint32_t r1_named_gpio_open(generic_device_registry_device *device);
#endif
