/* Offline bindings: GPIO helpers independent C; configure is pinned public PDL.
 * Valid request subset0/1/2/3/5/6; mode7 requires separate dither closure. */
#include "mode.h"
#include "../pin_control_offline/pins.h"
extern uint32_t Cy_MSCLP_Configure(volatile uint32_t *,const void *,uint32_t,void *);
static const touch_mode_dependencies dependencies={touch_mode_ios,touch_mode_shield,touch_mode_cmod,Cy_MSCLP_Configure,0};
uint32_t touch_switch_regular_dependency(uint32_t desired,uint8_t *c){return touch_switch_mode(desired,c,&dependencies);}
