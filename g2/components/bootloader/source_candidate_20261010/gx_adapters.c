/* SPDX-License-Identifier: MIT. Native adapters; no callback success stubs. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t native_spot_temperature_range(float);
extern uint32_t native_spot_buck_deepsleep_scan(uint32_t *,uint8_t);
extern void native_spot_transition_effect(uint8_t,uint8_t);
extern int native_spot_state_decode(const uint8_t *,uint32_t *,uint32_t *);
extern uint32_t native_spot_state_transition(uint32_t,uint32_t,uint32_t,uint32_t);
typedef struct { uint32_t words[4]; uint8_t temperature,state,auxiliary; } gx_decode_input;
_Static_assert(offsetof(gx_decode_input,temperature)==16,"temperature");
_Static_assert(offsetof(gx_decode_input,state)==17,"state");
_Static_assert(offsetof(gx_decode_input,auxiliary)==18,"auxiliary");
_Static_assert(sizeof(gx_decode_input)==20,"aligned decoder input");
uint8_t event_child_temperature_range(float f){return native_spot_temperature_range(f);}
void event_child_buck_deepsleep_scan(uint32_t *p,uint8_t t){(void)native_spot_buck_deepsleep_scan(p,t);}
void event_child_transition_effect(uint8_t n,uint8_t o){native_spot_transition_effect(n,o);}
int event_child_state_decode(const uint32_t *p,uint8_t t,uint8_t s,uint8_t a,uint32_t *major,uint32_t *minor){
 gx_decode_input input={{p[0],p[1],p[2],p[3]},t,s,a};
 return native_spot_state_decode((const uint8_t *)&input,major,minor);
}
void event_child_state_transition(uint32_t n,uint32_t o,uint32_t nm,uint32_t om){(void)native_spot_state_transition(n,o,nm,om);}
/* Literal configuration word434164 is zero in authenticated f89a4c46.
 * Source-defined data, never executable firmware bytes. */
__attribute__((section(".rodata.opencfw_gx_cfg"),used)) const uint32_t opencfw_gx_config_word=0;
