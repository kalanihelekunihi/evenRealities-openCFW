/* Stock Main 0x5edb68: positive file size or zero on open/seek/tell failure. */
#include <stdint.h>
extern void *audio_file_open(const char *,const char *);
extern int32_t audio_file_seek(void *,int32_t,uint32_t);
extern int32_t audio_file_tell(void *);
extern int32_t audio_file_close(void *);

uint32_t audio_tracepoint_file_size_5edb68(const char *path) {
    void *file=audio_file_open(path,"rb");
    if(file==0) return 0u;
    int32_t size=0;
    if(audio_file_seek(file,0,2u)==0) size=audio_file_tell(file);
    (void)audio_file_close(file);
    return size>0 ? (uint32_t)size : 0u;
}
