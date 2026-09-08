/* SPDX-License-Identifier: MIT */
/* Typed parameter data recovered against NationalChip lvp_param.h at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-PARAMETERS-NOTICE.txt.
 * The labels are vocabulary indices; their vocabulary/model is separate work. */
#include <stddef.h>
#include <wakeword-upstream-types.h>
_Static_assert(sizeof(LVP_KWS_PARAM) == 88, "shipped parameter configuration");
_Static_assert(offsetof(LVP_KWS_PARAM, kws_words) == 0, "word offset");
_Static_assert(offsetof(LVP_KWS_PARAM, labels) == 40, "label offset");
_Static_assert(offsetof(LVP_KWS_PARAM, label_length) == 72, "length offset");
_Static_assert(offsetof(LVP_KWS_PARAM, threshold) == 76, "threshold offset");
_Static_assert(offsetof(LVP_KWS_PARAM, kws_value) == 80, "event offset");
_Static_assert(offsetof(LVP_KWS_PARAM, major) == 84, "major offset");
LVP_KWS_PARAM open_cfw_gx8002_wakeword_parameters[2] = {
    {.kws_words = "hey_even", .labels = {54, 54}, .label_length = 2,
     .threshold = 567, .kws_value = 100, .major = 1},
    {.kws_words = "hi_even", .labels = {54, 54}, .label_length = 2,
     .threshold = 460, .kws_value = 101, .major = 1}
};
