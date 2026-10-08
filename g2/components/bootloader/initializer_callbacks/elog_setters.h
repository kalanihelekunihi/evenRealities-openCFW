#ifndef OPENCFW_BOOT_ELOG_SETTERS_H
#define OPENCFW_BOOT_ELOG_SETTERS_H
#include <stdint.h>
/* Reconstructed stock ABI. Legacy names are retained for existing callers. */
void opencfw_bl_service_mode(uint32_t enabled);
void opencfw_bl_service_enable(uint32_t enabled);
void opencfw_bl_invalid_pin_configure(uint32_t level,uint32_t format);
void opencfw_bl_service_configure(uint32_t level);
void opencfw_boot_elog_assert(const char *condition,const char *function,uint32_t line);
void opencfw_boot_elog_reset_request(void);
#endif
