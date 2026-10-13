#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
static int32_t ext247_div(uint32_t a,uint32_t b){int32_t r;__asm__("sdiv %0, %1, %2":"=r"(r):"r"(a),"r"(b));return r;}
static void ext247_store(uint32_t data,uint32_t index,uint32_t v){*(volatile uint32_t *)(uintptr_t)(data+index*4u)=v;}
/* Native514504..5147b0: padding, allocation or reuse, chain packet and rebound tail. */
int32_t audio_uart_nema_extend_bound_514504(uint32_t pairs){
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list){audio_uart_nema_error_set_4b127c(128u);return -1;}
 uint32_t flags=((volatile uint8_t *)list)[24];
 if(!(flags&2u)){audio_uart_nema_error_set_4b127c(8u);return -1;}
 uint32_t delta;
 if(flags&32u){uint32_t sector=list[11],used=list[5];delta=sector-used+sector*(uint32_t)ext247_div(used,sector);}
 else {uint32_t capacity=list[4],used=list[5];delta=capacity-used;}
 int32_t padding=(int32_t)((uint32_t)((int32_t)(delta+(delta>>31))>>1)-2u);
 if(padding>0){
  uint32_t n=(uint32_t)padding;
  for(uint32_t i=0;i<(n&3u);i++){uint32_t k=list[5];ext247_store(list[2],k,65536u);k++;ext247_store(list[2],k,0);list[5]=k+1u;}
  for(uint32_t i=0;i<(n>>2);i++){
   uint32_t k=list[5];ext247_store(list[2],k,65536u);k++;ext247_store(list[2],k,0);k++;
   uint32_t data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);k++;
   data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);k++;
   data=list[2];list[5]=k;ext247_store(data,k,65536u);k++;ext247_store(list[2],k,0);list[5]=k+1u;
  }
 }
 volatile uint32_t *node=(volatile uint32_t *)(uintptr_t)list[8];
 if(!node){
  node=audio_uart_nema_node_allocate_51416c(60u);if(!node){audio_uart_nema_error_set_4b127c(16u);return -1;}
  uint32_t bytes=(pairs+2u)*8u;uint32_t large=(int32_t)bytes>1024;
  uint32_t desc[4];audio_uart_nema_buffer_create_514070(desc,0u,large?bytes:1024u);
  node[0]=desc[0];node[1]=desc[1];node[2]=desc[2];node[3]=desc[3];node[4]=(uint32_t)((int32_t)desc[0]/8)*2u;
  node[5]=0;node[6]=large?0u:2u;node[9]=0;node[7]=UINT32_MAX;node[13]=UINT32_MAX;node[14]=UINT32_MAX;
  uint32_t data=node[2];node[10]=0;node[11]=0;node[12]=0;node[8]=0;
  if(!data){audio_uart_nema_error_set_4b127c(16u);audio_uart_nema_cl_node_release_514178((void *)node);return -1;}
  context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
  uint32_t root=list[9];node[9]=root?root:(uint32_t)(uintptr_t)list;
  list=(volatile uint32_t *)(uintptr_t)context[1];node[6]=list[6]&~12u;
 }
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
 if(!list)audio_uart_nema_error_set_4b127c(8192u);else list[6]=list[6]|4u;
 context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];list=(volatile uint32_t *)(uintptr_t)context[1];
 uint32_t k=list[5];ext247_store(list[2],k,240u);k++;uint32_t physical=node[3];ext247_store(list[2],k,physical);k++;
 uint32_t data=list[2];list[5]=k;ext247_store(data,k,244u);k++;uint32_t capacity=node[4];ext247_store(list[2],k,capacity);list[5]=k+1u;list[8]=(uint32_t)(uintptr_t)node;
 if(((volatile uint8_t *)node)[12]&7u){audio_uart_nema_error_set_4b127c(16384u);return 0;}
 list=(volatile uint32_t *)(uintptr_t)context[1];
 if(list){uint32_t used=list[5],cap=list[4];if((int32_t)cap>=(int32_t)(used+2u)){data=list[2];ext247_store(data,used,327680u);ext247_store(data+4u,used,0);list[6]=list[6]&~8u;}list[6]=list[6]&~32u;}
 context[1]=0;
 while(((volatile uint8_t *)node)[24]&4u)node=(volatile uint32_t *)(uintptr_t)node[8];
 context[1]=(uint32_t)(uintptr_t)node;return 0;
}
