/* SPDX-License-Identifier: MIT */
/* Source-owned storage for the recovered NationalChip TWS task queue.
 * Seven 8-byte records, as passed by the decoded TWS initializer.
 * See NATIONALCHIP-TWS-NOTICE.txt. */
#include <stddef.h>
#include <lvp_queue.h>
_Static_assert(sizeof(LVP_QUEUE)==20,"queue ABI");
_Static_assert(offsetof(LVP_QUEUE,buffer)==8,"queue buffer ABI");
LVP_QUEUE open_cfw_gx8002_active_snpu_queue
    __attribute__((section(".bss.active_snpu_queue")));
unsigned char open_cfw_gx8002_active_snpu_buffer[56]
    __attribute__((section(".bss.active_snpu_buffer")));
