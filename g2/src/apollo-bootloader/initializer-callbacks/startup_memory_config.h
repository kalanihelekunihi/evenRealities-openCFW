#ifndef OPENCFW_STARTUP_MEMORY_CONFIG_H
#define OPENCFW_STARTUP_MEMORY_CONFIG_H
#include <stdint.h>
/* R1 is an ambient input that stock preserves in its 64-bit return. */
uint64_t opencfw_boot_startup_mcu_memory(const uint8_t config[5]);
uint64_t opencfw_boot_startup_mcu_memory_core(const uint8_t config[5],
                                              uint32_t ambient_r1);
uint32_t opencfw_boot_startup_shared_memory(const uint8_t config[5]);
#endif
