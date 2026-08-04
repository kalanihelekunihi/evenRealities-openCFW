struct open_cfw_lv_tick_state;
extern struct open_cfw_lv_tick_state open_cfw_test_lv_tick_state;

#define OPEN_CFW_LV_TICK_STATE (&open_cfw_test_lv_tick_state)
#include "../../components/apollo_main/core_overlay/lv_tick.c"

struct open_cfw_lv_tick_state open_cfw_test_lv_tick_state;
