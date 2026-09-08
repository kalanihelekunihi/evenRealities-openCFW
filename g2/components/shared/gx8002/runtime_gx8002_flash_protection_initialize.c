/* SPDX-License-Identifier: MIT */
/* Recovered package0x166d8: publish three ordered protection descriptors. */
#include "runtime_gx8002_flash_protection_tables.h"
extern volatile uintptr_t open_cfw_gx8002_flash_protection_profiles[6];
void open_cfw_gx8002_flash_protection_initialize(void)
{
    volatile uintptr_t *profiles=open_cfw_gx8002_flash_protection_profiles;
    profiles[0]=(uintptr_t)open_cfw_gx8002_flash_protection_256k;
    profiles[1]=5;
    profiles[2]=(uintptr_t)open_cfw_gx8002_flash_protection_512k;
    profiles[3]=7;
    profiles[4]=(uintptr_t)open_cfw_gx8002_flash_protection_1024k;
    profiles[5]=9;
}
