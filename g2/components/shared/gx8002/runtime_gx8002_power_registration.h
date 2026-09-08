/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_POWER_REGISTRATION_H
#define OPEN_CFW_GX8002_POWER_REGISTRATION_H
#include <stdint.h>
#include <stddef.h>
struct open_cfw_app_power_registration {
    int (*callback)(void *);
    void *private_data;
};
struct open_cfw_gx8002_power_state {
    unsigned char unrecovered_header[8];
    uint32_t suspend_count;
    uint32_t resume_count;
    struct open_cfw_app_power_registration suspend[8];
    struct open_cfw_app_power_registration resume[8];
};
#ifndef OPEN_CFW_GX8002_POWER_HOST_TEST
_Static_assert(sizeof(struct open_cfw_app_power_registration)==8,"registration ABI");
_Static_assert(offsetof(struct open_cfw_gx8002_power_state,suspend)==16,"suspend offset");
_Static_assert(offsetof(struct open_cfw_gx8002_power_state,resume)==80,"resume offset");
#endif
extern struct open_cfw_gx8002_power_state open_cfw_gx8002_power_state;
int open_cfw_gx8002_register_suspend(struct open_cfw_app_power_registration *);
int open_cfw_gx8002_register_resume(struct open_cfw_app_power_registration *);
#endif
