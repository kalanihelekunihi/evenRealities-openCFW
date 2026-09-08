/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/vui/kws/kws_strategy.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-KWS-NOTICE.txt. */
#include <stddef.h>
#include <kws-upstream-types.h>
extern int printf(const char *, ...);
extern const char open_cfw_gx8002_kws_overflow_message[];
extern struct {
    int total;
    LVP_ACTIVATION_KWS activation_kws[8];
} open_cfw_gx8002_activation_list;
_Static_assert(sizeof(LVP_ACTIVATION_KWS) == 20, "activation entry size");
_Static_assert(offsetof(LVP_ACTIVATION_KWS, kws_score) == 8, "score offset");
_Static_assert(offsetof(LVP_ACTIVATION_KWS, reverse) == 16, "pointer offset");
_Static_assert(sizeof(open_cfw_gx8002_activation_list) == 164, "activation list size");
void KwsStragegyInsertKwsActivation(int kws_index, int kws_value,
                                  float kws_score, int score_index, void *priv)
{
    for (int i = 0; i < open_cfw_gx8002_activation_list.total; i++) {
        LVP_ACTIVATION_KWS *entry = &open_cfw_gx8002_activation_list.activation_kws[i];
        if (entry->kws_value == kws_value && entry->kws_index == kws_index) {
            if (kws_score > entry->kws_score)
                entry->kws_score = kws_score;
            return;
        }
    }
    int index = open_cfw_gx8002_activation_list.total;
    if ((size_t)index >= sizeof(open_cfw_gx8002_activation_list.activation_kws) / sizeof(LVP_ACTIVATION_KWS)) {
        printf(open_cfw_gx8002_kws_overflow_message);
        return;
    }
    volatile LVP_ACTIVATION_KWS *entry = &open_cfw_gx8002_activation_list.activation_kws[index];
    entry->kws_index = kws_index;
    entry->kws_value = kws_value;
    entry->kws_score = kws_score;
    entry->score_index = score_index;
    entry->reverse = priv;
    *(volatile int *)&open_cfw_gx8002_activation_list.total = index + 1;
}
