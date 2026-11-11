/* Audio thread terminate 0x53c4f2. AUD_ThreadInit/AUD_ResourceInit live in
 * drivers/codec-host/audio-thread-codec/thread_audio_codec_ctrl.c. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_audio_dispatch_state[] __asm__("g2_audio_dispatch_state");
extern int32_t audio_thread_terminate_peer(void*);
/* Stock 0x53C4F2 (aud_thread_terminate) */
void audio_thread_terminate_selected(void){
 void *thread=*(void**)((uint32_t)(uintptr_t)g2ref_g2_audio_dispatch_state+0x8u);
 if(thread){audio_thread_terminate_peer(thread);*(void**)((uint32_t)(uintptr_t)g2ref_g2_audio_dispatch_state+0x8u)=0;}
}
