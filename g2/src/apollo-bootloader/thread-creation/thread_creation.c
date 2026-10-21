/* SPDX-License-Identifier: MIT
 * Independent reconstruction of stock 0x4160fe..0x4161c6.
 * Kernel allocation/scheduling providers remain explicit, not implemented here.
 */
#include <stdint.h>
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_kernel_static_thread(uintptr_t entry, uintptr_t name,
    uint32_t words, uintptr_t arg, uint32_t priority, uintptr_t stack,
    uintptr_t control_block);
extern uint32_t opencfw_bl_kernel_dynamic_thread(uintptr_t entry, uintptr_t name,
    uint32_t words, uintptr_t arg, uint32_t priority, uint32_t *handle);
uint32_t opencfw_boot_thread_new(uintptr_t entry, uintptr_t arg,
                              const uint32_t *attr)
{
    uint32_t handle=0, priority=24, words=256;
    uintptr_t name=0;
    int32_t path=-1;
    if (opencfw_bl_context_guard() || !entry) return 0;
    if (attr) {
        if (attr[0]) name=attr[0];
        if (attr[6]) priority=attr[6];
        if (!priority || priority>=57 || (attr[1]&1)) return 0;
        if (attr[5]) words=attr[5]>>2;
        if (attr[2] && attr[3]>=112 && attr[4] && attr[5]) path=1;
        else if (!attr[2] && !attr[3] && !attr[4]) path=0;
    } else path=0;
    if (path==1) {
        handle=opencfw_bl_kernel_static_thread(entry,name,words,arg,priority,
                                              attr[4],attr[2]);
    } else if (path==0) {
        if (opencfw_bl_kernel_dynamic_thread(entry,name,(uint16_t)words,arg,
                                             priority,&handle)!=1) handle=0;
    }
    return handle;
}
