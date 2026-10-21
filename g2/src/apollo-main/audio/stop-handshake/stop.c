/* Logger-disabled first-party stop coordination, no timer in selected exit contract. */
#include <stdint.h>
extern uint32_t audio_flags_set(void*,uint32_t);
extern void audio_ack_index(uint32_t),audio_queue_delete_peer(void*),audio_delay(uint32_t);
extern uint32_t audio_event_wait(void*,uint32_t,uint32_t,uint32_t);
uint32_t audio_stop_fanout(uint32_t reason){
 const uint32_t ctx[10]={0x200040fc,0x20004120,0x20004044,0x20003ffc,0x20004020,0x20004068,0x20003f98,0x2000408c,0x20003664,0x20000658};
 const uint32_t bits[10]={2,0x40,0x800,0x80,0x100,0x200,8,0x10,0x20,0x1000};uint32_t want=0;
 for(uint32_t i=0;i<10;i++){if((reason&0x20)&&i>=3&&i<=5)continue;want|=bits[i];audio_flags_set(*(void**)(ctx[i]+8),0x800000);}
 return want;
}
void audio_stop_one(void *thread,uint32_t index){
 audio_flags_set(thread,0x800000);audio_event_wait(*(void**)0x200040f4u,1u<<index,1,20000);
}
void audio_exit_no_timer(void){
 audio_ack_index(3);void *q=*(void**)0x20003fa4u;
 if(q){audio_queue_delete_peer(q);*(void**)0x20003fa4u=0;}
 for(;;)audio_delay(0xffffffffu);
}
