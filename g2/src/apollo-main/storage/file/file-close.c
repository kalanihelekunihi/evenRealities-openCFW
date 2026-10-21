#include <stdint.h>
extern int32_t audio_file_mutex_acquire(void*,uint32_t),audio_file_mutex_release(void*);
extern int32_t audio_file_backend_close(void*,void*);
extern void audio_file_heap_free(void*);
int32_t audio_file_close_selected(uint32_t *stream){
 void **mutex=(void**)0x200748f4u;
 if(audio_file_mutex_acquire(*mutex,1000)!=0)return -1;
 int32_t result=audio_file_backend_close((void*)stream[0],stream+1);
 audio_file_mutex_release(*mutex);
 audio_file_heap_free(stream);
 return result<0?-1:0;
}
