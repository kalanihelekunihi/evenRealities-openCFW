#ifndef OPENCFW_STARTUP_SHUTDOWN_H
#define OPENCFW_STARTUP_SHUTDOWN_H
#include <stdint.h>
uint32_t opencfw_boot_startup_shutdown_first(void);
uint32_t opencfw_boot_startup_shutdown_second(void);
uint32_t opencfw_boot_shutdown_prepare(void);
uint32_t opencfw_boot_shutdown_wait_clear(void);
uint32_t opencfw_boot_shutdown_wait_slot(uint32_t slot);
uint32_t opencfw_boot_shutdown_wait_zero(void);
uint32_t opencfw_boot_shutdown_clock_release(void);
uint32_t opencfw_boot_shutdown_resource(uint32_t enable);
uint32_t opencfw_boot_shutdown_debug_release(void);
#endif
