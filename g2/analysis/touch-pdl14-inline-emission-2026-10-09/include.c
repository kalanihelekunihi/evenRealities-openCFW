/* Analysis emission unit: no implementation or executable wrapper added. */
#include "cy_sysclk.h"
#include "cy_scb_common.h"
/* Address-taking forces real always-inline definitions to have callable bodies. */
cy_en_sysclk_dividers_t (*const analysis_get_divider)(void) = Cy_SysClk_ClkHfGetDivider;
void (*const analysis_set_divider)(cy_en_sysclk_dividers_t) = Cy_SysClk_ClkHfSetDivider;
void (*const analysis_rx_level)(CySCB_Type *, uint32_t) = Cy_SCB_SetRxFifoLevel;
