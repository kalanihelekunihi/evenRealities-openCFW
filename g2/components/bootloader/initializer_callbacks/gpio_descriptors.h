/* Locked bootloader GPIO descriptor and directly required child interfaces. */
#ifndef OPENCFW_BOOT_GPIO_DESCRIPTORS_H
#define OPENCFW_BOOT_GPIO_DESCRIPTORS_H
#include <stdint.h>
typedef struct { uint32_t pin; uint8_t type, initial, interrupt_mode, reserved; uint32_t callback; } opencfw_boot_gpio_descriptor;
_Static_assert(sizeof(opencfw_boot_gpio_descriptor)==12,"locked descriptor stride");
uint32_t opencfw_bl_descriptor_register(const opencfw_boot_gpio_descriptor *,uint32_t);
uint32_t opencfw_boot_gpio_mask_status(uint32_t channel,uint32_t enabled,uint32_t *mask);
uint32_t opencfw_boot_gpio_mask_clear(uint32_t channel,const uint32_t *mask);
uint32_t opencfw_boot_gpio_callback_register(uint32_t channel,uint32_t pin,uint32_t callback,uint32_t argument);
uint32_t opencfw_boot_gpio_interrupt_control(uint32_t channel,uint32_t control,const uint32_t *input);
void opencfw_boot_gpio_priority(uint32_t interrupt,uint32_t priority);
extern const opencfw_boot_gpio_descriptor opencfw_boot_gpio_descriptors[97];
#endif
