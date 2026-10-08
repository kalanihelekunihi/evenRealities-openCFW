#ifndef OPENCFW_STARTUP_MEMORY_CONFIG_H
#define OPENCFW_STARTUP_MEMORY_CONFIG_H
#include <stdint.h>
uint32_t opencfw_boot_startup_mcu_memory(const uint8_t config[5]);
uint32_t opencfw_boot_startup_shared_memory(const uint8_t config[5]);
#endif
