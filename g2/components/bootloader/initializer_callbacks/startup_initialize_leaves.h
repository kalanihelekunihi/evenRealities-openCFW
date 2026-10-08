#ifndef OPENCFW_STARTUP_INITIALIZE_LEAVES_H
#define OPENCFW_STARTUP_INITIALIZE_LEAVES_H
#include <stdint.h>
uint32_t opencfw_boot_startup_sleep_fields_write(uint32_t packed);
void opencfw_boot_startup_sleep_fields_read(uint8_t output[3]);
uint32_t opencfw_boot_startup_hook20(void);
uint32_t opencfw_boot_startup_hook24(uint32_t first,uint32_t second);
uint32_t opencfw_boot_startup_hook28(void);
uint32_t opencfw_boot_startup_hook30(void);
uint32_t opencfw_boot_startup_hook34(void);
uint32_t opencfw_boot_startup_hook38(void);
#endif
