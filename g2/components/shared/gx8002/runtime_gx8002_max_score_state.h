/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_MAX_SCORE_STATE_H
#define OPEN_CFW_GX8002_MAX_SCORE_STATE_H
#include <stdint.h>
#include <stddef.h>
/* Recovered from MAX scorer stock accesses; target addresses belong in linker script. */
struct open_cfw_gx8002_max_score_state {
    uint8_t activation[2];
    int32_t window_index;
    int32_t window[10][2];
    uint32_t keyword_count;
    void *keyword_parameters;
    int32_t maximum_score;
};
_Static_assert(offsetof(struct open_cfw_gx8002_max_score_state,window_index)==4,"MAX index");
_Static_assert(offsetof(struct open_cfw_gx8002_max_score_state,window)==8,"MAX window");
_Static_assert(offsetof(struct open_cfw_gx8002_max_score_state,keyword_count)==88,"MAX count");
_Static_assert(offsetof(struct open_cfw_gx8002_max_score_state,keyword_parameters)==92,"MAX parameters");
_Static_assert(offsetof(struct open_cfw_gx8002_max_score_state,maximum_score)==96,"MAX score");
_Static_assert(sizeof(struct open_cfw_gx8002_max_score_state)==100,"MAX state size");
extern struct open_cfw_gx8002_max_score_state open_cfw_gx8002_max_score_state;
#endif
