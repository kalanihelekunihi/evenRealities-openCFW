/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/vui/kws/max_decoder.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-MAX-NOTICE.txt. */
#include <max-init-upstream-types.h>
extern int printf(const char *, ...);
extern void KwsStrategyInit(void);
extern LVP_KWS_PARAM_LIST open_cfw_gx8002_max_keyword_list;
const char open_cfw_gx8002_max_init_error[] __attribute__((aligned(1))) =
    "[LVP_MAX_DECODE]==ERROR== The activation_flag space is too small\n";
void LvpInitMaxKws(void)
{
    if (open_cfw_gx8002_max_keyword_list.count != 2)
        printf(open_cfw_gx8002_max_init_error);
    KwsStrategyInit();
}
