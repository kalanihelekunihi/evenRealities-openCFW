/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws max_decoder.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-MAX-NOTICE.txt. */
#include <max-list-upstream-types.h>
#include <stddef.h>
extern int printf(const char *, ...);
extern LVP_KWS_PARAM open_cfw_gx8002_wakeword_parameters[2];
LVP_KWS_PARAM_LIST open_cfw_gx8002_max_keyword_list;
_Static_assert(sizeof(LVP_KWS_PARAM_LIST) == 8, "list state size");
_Static_assert(offsetof(LVP_KWS_PARAM_LIST, kws_param_list) == 4, "list pointer offset");
#define MESSAGE(name, text) const char name[] __attribute__((aligned(1))) = text
MESSAGE(open_cfw_gx8002_max_list_header, "[LVP_MAX_DECODE]Demo Kws List [Total:%d]:\n");
MESSAGE(open_cfw_gx8002_max_list_word, "[LVP_MAX_DECODE]KWS: %s | ");
MESSAGE(open_cfw_gx8002_max_list_value, "KV: %02d | ");
MESSAGE(open_cfw_gx8002_max_list_threshold, "TRH: %02d | ");
MESSAGE(open_cfw_gx8002_max_list_newline, "\n");
void LvpPrintMaxKwsList(void)
{
    open_cfw_gx8002_max_keyword_list.count = 2;
    open_cfw_gx8002_max_keyword_list.kws_param_list = open_cfw_gx8002_wakeword_parameters;
    printf(open_cfw_gx8002_max_list_header, open_cfw_gx8002_max_keyword_list.count);
    for (unsigned int i = 0; i < open_cfw_gx8002_max_keyword_list.count; ++i) {
        printf(open_cfw_gx8002_max_list_word, open_cfw_gx8002_max_keyword_list.kws_param_list[i].kws_words);
        printf(open_cfw_gx8002_max_list_value, open_cfw_gx8002_max_keyword_list.kws_param_list[i].kws_value);
        printf(open_cfw_gx8002_max_list_threshold, open_cfw_gx8002_max_keyword_list.kws_param_list[i].threshold);
        printf(open_cfw_gx8002_max_list_newline);
    }
}
