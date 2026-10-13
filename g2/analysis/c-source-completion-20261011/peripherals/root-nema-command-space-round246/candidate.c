#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern int32_t audio_uart_nema_extend_bound_514504(uint32_t);
static int32_t space246_div(uint32_t a,uint32_t b){int32_t r;__asm__("sdiv %0, %1, %2":"=r"(r):"r"(a),"r"(b));return r;}
/* Native514aec..514b76: pair reservation with sector rollover or list extension. */
void *audio_uart_nema_cl_get_space_514aec(uint32_t pairs){
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list){audio_uart_nema_error_set_4b127c(128u);return 0;}
 list[6]=list[6]&~8u;
 uint32_t remaining;
 if(((volatile uint8_t *)list)[24]&32u){uint32_t sector=list[11],used=list[5];remaining=sector-used+sector*(uint32_t)space246_div(used,sector);}
 else {uint32_t capacity=list[4],used=list[5];remaining=capacity-used;}
 uint32_t half=(uint32_t)((int32_t)(remaining+(remaining>>31))>>1);
 if(((volatile uint8_t *)list)[24]&32u){
  if((int32_t)half<(int32_t)(pairs+1u)){
   ((volatile uint8_t *)context)[249]=0;
   context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
   audio_uart_nema_sector_rollover_5147b0((void *)(uintptr_t)context[1]);
  }
 }else if((int32_t)(half-2u)<(int32_t)pairs){if(audio_uart_nema_extend_bound_514504(pairs)<0)return 0;}
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 list=(volatile uint32_t *)(uintptr_t)context[1];uint32_t used=list[5],data=list[2];
 uint32_t pointer=data+used*4u;list[5]=used+pairs*2u;return (void *)(uintptr_t)pointer;
}
