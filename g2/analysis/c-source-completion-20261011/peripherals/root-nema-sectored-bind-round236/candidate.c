#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
static int32_t bind236_div(uint32_t a,uint32_t b) {
 int32_t result;__asm__("sdiv %0, %1, %2":"=r"(result):"r"(a),"r"(b));return result;
}
/* Native5143d4..5144ba: G2 sector negotiation and cached previous-list unbind. */
void audio_uart_nema_cl_bind_sectored_5143d4(void *cell,uint32_t sectors) {
 volatile uint32_t *list=cell;
 if(!list){audio_uart_nema_error_set_4b127c(8192u);return;}
 if(((volatile uint8_t *)list)[12]&7u){audio_uart_nema_error_set_4b127c(16384u);return;}
 uint32_t parent=list[9];if(parent)list=(volatile uint32_t *)(uintptr_t)parent;
 if((int32_t)sectors<2)sectors=2;
 else if((int32_t)sectors>2){
  uint32_t bytes=list[4]*4u;int32_t quotient=bind236_div(bytes,sectors);
  if(quotient<512){
   if(sectors&1u)sectors++;
   while((int32_t)sectors>=4){sectors-=2;quotient=bind236_div(bytes,sectors);if(quotient>=512)break;}
   if(quotient<512){audio_uart_nema_error_set_4b127c(65536u);return;}
  }
 }
 uint32_t bytes=list[4]*4u;uint32_t quotient=(uint32_t)bind236_div(bytes,sectors);
 if(bytes-sectors*quotient){audio_uart_nema_error_set_4b127c(16384u);return;}
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *previous=(volatile uint32_t *)(uintptr_t)context[1];
 if(previous){
  uint32_t used=previous[5],capacity=previous[4];
  if((int32_t)capacity>=(int32_t)(used+2u)){
   uint32_t data=previous[2];
   *(volatile uint32_t *)(uintptr_t)(data+used*4u)=0x00050000u;
   *(volatile uint32_t *)(uintptr_t)(data+4u+used*4u)=0;
   previous[6]=previous[6]&~8u;
  }
  previous[6]=previous[6]&~32u;context[1]=0;
 }
 list[6]=list[6]|32u;list[13]=UINT32_MAX;list[14]=UINT32_MAX;
 uint32_t words=(uint32_t)bind236_div(list[4],sectors);if(words&1u)words--;
 list[11]=words;list[10]=sectors;list[12]=0;
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];context[1]=(uint32_t)(uintptr_t)list;
}
