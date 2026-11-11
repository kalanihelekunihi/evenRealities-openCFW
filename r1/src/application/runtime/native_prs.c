/* Recovered single-box PRS configuration. The pinned Nordic implementation
 * remains unchanged; only UARTE0/UART0 box 4 is present in the stock lookup.
 * Ownership/state and exactness evidence: prs-c-review.md. */
#include <nrfx.h>
#undef NRFX_PRS_ENABLED
#define NRFX_PRS_ENABLED 1
#undef NRFX_PRS_BOX_0_ENABLED
#define NRFX_PRS_BOX_0_ENABLED 0
#undef NRFX_PRS_BOX_1_ENABLED
#define NRFX_PRS_BOX_1_ENABLED 0
#undef NRFX_PRS_BOX_2_ENABLED
#define NRFX_PRS_BOX_2_ENABLED 0
#undef NRFX_PRS_BOX_3_ENABLED
#define NRFX_PRS_BOX_3_ENABLED 0
#undef NRFX_PRS_BOX_4_ENABLED
#define NRFX_PRS_BOX_4_ENABLED 1
#undef NRFX_PRS_CONFIG_LOG_ENABLED
#define NRFX_PRS_CONFIG_LOG_ENABLED 0
#include "prs/nrfx_prs.c"
