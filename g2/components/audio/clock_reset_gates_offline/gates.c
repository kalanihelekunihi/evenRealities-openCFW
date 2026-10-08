#include "gates.h"
#define W(a) (*(volatile uint32_t *)(a))
uint32_t clock_reset_should_enter(void){return !(W(0x4000885c)&2)&&(W(0x40008858)>>16)==0x5af0;}
uint32_t clock_reset_has_requests(void){return (W(0x40008858)&63)!=0;}
void clock_reset_reinitialize_retained(void){W(0x40008858)=0;W(0x40008858)=(W(0x40008858)&65535)|0x5af00000;}

/* Precondition: active recovery is gated out or low-six request bits are zero. */
void clock_reset_gated_path(void){clock_reset_reinitialize_retained();}
