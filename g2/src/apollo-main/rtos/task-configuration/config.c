/* Audio thread terminate 0x53c4f2. AUD_ThreadInit/AUD_ResourceInit live in
 * drivers/codec-host/audio-thread-codec/thread_audio_codec_ctrl.c. */
#include <stdint.h>
extern int32_t audio_thread_terminate_peer(void*);
/* Stock 0x53C4F2 (aud_thread_terminate) */
void audio_thread_terminate_selected(void){
 void *thread=*(void**)0x20003fa0u;
 if(thread){audio_thread_terminate_peer(thread);*(void**)0x20003fa0u=0;}
}
