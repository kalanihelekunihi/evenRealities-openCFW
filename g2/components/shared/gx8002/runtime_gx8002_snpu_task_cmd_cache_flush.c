/* SPDX-License-Identifier: MIT */
/* The descriptor header and nine base commands are separate clean ranges. */
#include <stdint.h>
extern void open_cfw_gx8002_dcache_clean_range(void *,uint32_t);
void open_cfw_gx8002_snpu_task_cmd_cache_flush(void *descriptor)
{
    open_cfw_gx8002_dcache_clean_range(descriptor,8);
    open_cfw_gx8002_dcache_clean_range((void *)((uintptr_t)descriptor+16),9u*12u);
}
