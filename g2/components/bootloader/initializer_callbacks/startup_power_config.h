#ifndef OPENCFW_STARTUP_POWER_CONFIG_H
#define OPENCFW_STARTUP_POWER_CONFIG_H
#include <stdint.h>
uint32_t opencfw_boot_startup_power_configure(uint32_t operation,uint32_t unused);
uint32_t opencfw_boot_startup_temperature(float *output,float input) __attribute__((pcs("aapcs-vfp")));
void opencfw_boot_startup_external_mode(uint32_t callback);
void opencfw_boot_startup_register_setup(void);
uint32_t opencfw_boot_startup_resource_ready(void);
uint32_t opencfw_boot_startup_hook_before(void);
uint32_t opencfw_boot_startup_hook_middle(void);
uint32_t opencfw_boot_startup_hook_after(void);
#endif
