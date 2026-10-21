#ifndef OPENCFW_STARTUP_RUNTIME_H
#define OPENCFW_STARTUP_RUNTIME_H
#include <stdint.h>
uint32_t opencfw_boot_startup_trim_version(uint32_t *output);
uint32_t opencfw_boot_startup_info_cache(void);
uint32_t opencfw_boot_startup_spot_dispatch(void);
#endif
