#include <stdint.h>
extern void audio_daemon_process_or_block(uint32_t,uint32_t),audio_daemon_drain_commands(void);
uint32_t audio_daemon_next_expiry(uint32_t *empty){
 uint32_t *l=*(uint32_t**)0x20074aa8u;*empty=l[0]==0;
 return *empty?0:**(uint32_t**)(l+3);
}
/* One iteration only; original task repeats this sequence forever. */
void audio_daemon_one_iteration(void){
 uint32_t empty,expiry=audio_daemon_next_expiry(&empty);
 audio_daemon_process_or_block(expiry,empty);
 audio_daemon_drain_commands();
}
extern void audio_daemon_initialize_queue(void),audio_daemon_get_static_memory(void**,void**,uint32_t*);
extern void *audio_daemon_create_static(void*,const char*,uint32_t,void*,uint32_t,void*,void*);
/* Contract: timer command queue already initialized, static-create succeeds in isolated boot fixture. */
uint32_t audio_daemon_create_selected(void){
 audio_daemon_initialize_queue();if(!*(void**)0x20074ab0u)return 0;
 void *tcb,*stack;uint32_t depth;audio_daemon_get_static_memory(&tcb,&stack,&depth);
 void *handle=audio_daemon_create_static((void*)0x47e879u,(const char*)0x78ebccu,depth,0,54,stack,tcb);
 *(void**)0x20074ab4u=handle;return handle!=0;
}
