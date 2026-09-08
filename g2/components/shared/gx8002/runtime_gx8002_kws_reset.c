/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws kws_strategy.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-KWS-NOTICE.txt. */
#include <stddef.h>
#include <kws-reset-upstream-types.h>
extern void *memset(void *, int, size_t);
struct {
    int total;
    LVP_ACTIVATION_KWS activation_kws[8];
} open_cfw_gx8002_activation_list;
_Static_assert(sizeof(open_cfw_gx8002_activation_list) == 164, "activation BSS extent");
__attribute__((noinline)) void KwsStrategyReset(void)
{
    memset(&open_cfw_gx8002_activation_list, 0, sizeof(open_cfw_gx8002_activation_list));
}
void KwsStrategyInit(void)
{
    KwsStrategyReset();
}
