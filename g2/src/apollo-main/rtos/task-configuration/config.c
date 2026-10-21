/* Logger-disabled thread initializer and queue creation prefix. Original OS peers retained. */
#include <stdint.h>
extern void *audio_thread_new(void(*)(void*),void*,const void*);
extern void *audio_queue_new(uint32_t,uint32_t,const void*);
void audio_thread_init_selected(void){
 *(void**)0x20003fa0u=audio_thread_new((void(*)(void*))0x53c52du,0,(const void*)0x75b8c8u);
}
void audio_resource_queue_prefix(void){
 /* Contract ends at allocation entry before this result/store; no timer continuation. */
 *(void**)0x20003fa4u=audio_queue_new(50,12,0);
}
extern int32_t audio_thread_terminate_peer(void*);
void audio_thread_terminate_selected(void){
 void *thread=*(void**)0x20003fa0u;
 if(thread){audio_thread_terminate_peer(thread);*(void**)0x20003fa0u=0;}
}
