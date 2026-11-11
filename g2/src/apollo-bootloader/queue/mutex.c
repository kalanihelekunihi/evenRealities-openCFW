/* SPDX-License-Identifier: MIT
 * Reconstructed mutex wrappers 0x4166AA..0x416762. Bit0 selects provider
 * variant; remaining bits are the kernel handle. No kernel revision claim.
 */
#include <stdint.h>
#include "queue_wrappers.h"
extern uint32_t opencfw_bl_kernel_mutex_take_tagged(uint32_t,uint32_t);
extern uint32_t opencfw_bl_kernel_mutex_take_plain(uint32_t,uint32_t);
extern uint32_t opencfw_bl_kernel_mutex_give_tagged(uint32_t);
extern uint32_t opencfw_bl_kernel_queue_put_blocking(void *,const void *,uint32_t,uint32_t);

int32_t opencfw_boot_mutex_acquire(uint32_t tagged_handle,uint32_t timeout)
{
    uint32_t handle=tagged_handle&~1u;
    if(opencfw_bl_queue_is_nonblocking_context())return -6;
    if(!handle)return -4;
    uint32_t result=(tagged_handle&1u)
        ?opencfw_bl_kernel_mutex_take_tagged(handle,timeout)
        :opencfw_bl_kernel_mutex_take_plain(handle,timeout);
    if(result==1u)return 0;
    return timeout ? -2 : -3;
}

int32_t opencfw_boot_mutex_release(uint32_t tagged_handle)
{
    uint32_t handle=tagged_handle&~1u;
    if(opencfw_bl_queue_is_nonblocking_context())return -6;
    if(!handle)return -4;
    uint32_t result=(tagged_handle&1u)
        ?opencfw_bl_kernel_mutex_give_tagged(handle)
        :opencfw_bl_kernel_queue_put_blocking((void *)(uintptr_t)handle,0,0,0);
    return result==1u ? 0 : -3;
}

/* Stock entry names that branch straight to the provider above. */
__typeof__(opencfw_boot_mutex_acquire) opencfw_provider_4166aa __attribute__((alias("opencfw_boot_mutex_acquire")));
__typeof__(opencfw_boot_mutex_release) opencfw_provider_416710 __attribute__((alias("opencfw_boot_mutex_release")));
__typeof__(opencfw_boot_mutex_acquire) opencfw_boot_fs_mutex_acquire __attribute__((alias("opencfw_boot_mutex_acquire")));
__typeof__(opencfw_boot_mutex_release) opencfw_boot_fs_mutex_release __attribute__((alias("opencfw_boot_mutex_release")));
