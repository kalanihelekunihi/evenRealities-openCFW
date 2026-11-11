#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_file_api_mutex[] __asm__("audio_file_api_mutex");
extern int32_t audio_file_mutex_acquire(void*,uint32_t),audio_file_mutex_release(void*);
extern int32_t audio_file_backend_close(void*,void*);
extern void audio_file_heap_free(void*);
/* Stock 0x4745F4 (file_close) */
int32_t audio_file_close_selected(uint32_t *stream){
 void **mutex=(void**)((uint32_t)(uintptr_t)g2ref_audio_file_api_mutex);
 if(audio_file_mutex_acquire(*mutex,1000)!=0)return -1;
 int32_t result=audio_file_backend_close((void*)stream[0],stream+1);
 audio_file_mutex_release(*mutex);
 audio_file_heap_free(stream);
 return result<0?-1:0;
}
