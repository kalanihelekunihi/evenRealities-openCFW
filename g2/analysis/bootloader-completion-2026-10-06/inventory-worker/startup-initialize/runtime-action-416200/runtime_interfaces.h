/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_RUNTIME_ACTION_INTERFACES_H
#define OPENCFW_RUNTIME_ACTION_INTERFACES_H
#include <stdint.h>
enum opencfw_thread_state { OPENCFW_RUNNING=0, OPENCFW_READY=1,
 OPENCFW_BLOCKED=2, OPENCFW_SUSPENDED=3, OPENCFW_DELETED=4 };
/* R0 is CMSIS-compatible status; R1 preserves original incomingR3. */
uint64_t opencfw_boot_runtime_action(uint32_t handle,uint32_t unused1,
                                    uint32_t unused2,uint32_t carry);
uint32_t opencfw_boot_thread_state(uint32_t *tcb);
void opencfw_boot_thread_delete(uint32_t *tcb);
void opencfw_boot_thread_release_storage(uint32_t *tcb);
#endif
