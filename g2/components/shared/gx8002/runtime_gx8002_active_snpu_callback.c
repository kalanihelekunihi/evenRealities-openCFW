/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip _LvpActiveSnpuCallback in lvp/lvp_mode_tws.c,
 * commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-STREAM-NOTICE.txt. Not yet admitted. */
#include <stddef.h>
#include <driver/gx_snpu.h>
#include <lvp_queue.h>
typedef struct { int module_id; void *priv; } ACTIVE_MODULE_INFO;
extern LVP_QUEUE open_cfw_gx8002_active_snpu_queue;
_Static_assert(sizeof(ACTIVE_MODULE_INFO)==8,"module queue record ABI");
_Static_assert(offsetof(ACTIVE_MODULE_INFO,priv)==4,"module private ABI");
int open_cfw_gx8002_active_snpu_callback(int module_id,GX_SNPU_STATE state,void *priv)
{
    (void)state;
    ACTIVE_MODULE_INFO info={module_id,priv};
    LvpQueuePut(&open_cfw_gx8002_active_snpu_queue,(const unsigned char *)&info);
    return 0;
}
