#ifndef OPENCFW_BOOT_SERVICE_RECORDS_H
#define OPENCFW_BOOT_SERVICE_RECORDS_H
#include <stdint.h>
uint32_t opencfw_bl_service_guard(void);
void opencfw_bl_service_commit(void);
void opencfw_boot_service_mutex_initialize(void);
void opencfw_boot_service_mutex_acquire(void);
void opencfw_boot_service_mutex_release(void);
void opencfw_bl_service_wake(void);
void opencfw_bl_service_sleep(void);
#endif
