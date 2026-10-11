/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006968 transport callback and worker registration.
 * Callback implementations are separate source obligations.
 */
#include <stdint.h>
#include "application_boot_transport_registration_data_candidate.h"
extern uint32_t case_boot_transport_register(uint32_t callback,uint32_t mode,
                                             uint32_t flags,uint32_t storage); /* 0xaa48 */
extern uint32_t case_boot_transport_worker(uint32_t callback,uint32_t mode,
                                           uint32_t storage); /* 0xa93c */
extern uint32_t case_boot_transport_event(uint32_t storage); /* 0xa836 */
extern void case_boot_transport_cb_9d70(void);
extern void case_boot_transport_cb_bb4c(void);
extern void case_boot_transport_cb_9684(void);
extern void case_boot_transport_cb_b7ec(void);
extern void case_boot_transport_cb_bb90(void);
extern void case_boot_transport_cb_ab70(void);
extern void case_boot_transport_cb_6e1c(void);
extern void case_boot_transport_cb_7f2c(void);
extern void case_policy_task_7200(void);
extern void case_boot_transport_cb_82ec(void);

void case_boot_transport_start(void)
{
    volatile uint32_t *shared=(volatile uint32_t *)(uintptr_t)0x200000b8u;
    uint32_t storage=(uint32_t)(uintptr_t)&case_boot_transport_registration_storage;
    shared[4u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_9d70,0u,0u,storage);
    shared[6u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_bb4c,1u,0u,storage+0x20u);
    shared[7u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_9684,1u,0u,storage+0x30u);
    shared[8u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_b7ec,1u,0u,storage+0x40u);
    shared[5u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_bb90,0u,0u,storage+0x10u);
    shared[9u]=case_boot_transport_register((uint32_t)(uintptr_t)case_boot_transport_cb_ab70,0u,0u,storage+0x50u);
    shared[11u]=case_boot_transport_worker((uint32_t)(uintptr_t)case_boot_transport_cb_6e1c,0u,storage+0x84u);
    shared[12u]=case_boot_transport_worker((uint32_t)(uintptr_t)case_boot_transport_cb_7f2c,0u,storage+0xa8u);
    shared[13u]=case_boot_transport_worker((uint32_t)(uintptr_t)case_policy_task_7200,0u,storage+0xccu);
    shared[10u]=case_boot_transport_worker((uint32_t)(uintptr_t)case_boot_transport_cb_82ec,0u,storage+0x60u);
    shared[14u]=case_boot_transport_event(storage+0xf0u);
}
