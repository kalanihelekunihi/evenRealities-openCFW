/* Native file facade 0x474550/0x474634/0x474814/0x474870.
 * The 96-byte FILE record holds the LittleFS context at +0 and lfs_file
 * state at +4. Global context/mutex are typed runtime cells. */
#include <stdint.h>

extern void *codec_allocate(uint32_t); /* 0x474cd2 */
extern void audio_file_heap_free(void *); /* 0x474d16 */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* 0x44981c */
extern int32_t audio_file_lfs_open(void *,void *,const char *,uint32_t); /* 0x4cfa94 */
extern int32_t audio_file_lfs_read(void *,void *,void *,uint32_t); /* 0x4cfb40 */
extern int32_t audio_file_lfs_seek(void *,void *,int32_t,uint32_t); /* 0x4cfbb2 */
extern int32_t audio_file_lfs_tell(void *,void *); /* 0x4cfbe8 */
extern uint8_t audio_file_lfs_context[]; /* RAM 0x20071ac8 */
extern void *audio_file_api_mutex; /* RAM 0x200748f4 */

static uint32_t contains(const char *string,char token) {
    for(;*string!=0;string++) if(*string==token) return 1u;
    return 0u;
}
static void *context(void *file) {
    return (void *)(uintptr_t)*(uint32_t *)file;
}
void *audio_file_open(const char *path,const char *mode) {
    uint8_t *file=(uint8_t *)codec_allocate(96u);
    if(file==0) return 0;
    *(uint32_t *)(void *)file=(uint32_t)(uintptr_t)audio_file_lfs_context;
    uint32_t flags=0u;
    if(contains(mode,'r')) flags|=1u;
    if(contains(mode,'w')) flags|=0x502u;
    if(contains(mode,'a')) flags|=0x902u;
    if(contains(mode,'+')) flags|=3u;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) {
        audio_file_heap_free(file);
        return 0;
    }
    int32_t status=audio_file_lfs_open(context(file),file+4u,path,flags);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if(status<0) {
        audio_file_heap_free(file);
        return 0;
    }
    return file;
}
uint32_t audio_file_read(void *buffer,uint32_t size,uint32_t count,void *file) {
    uint32_t bytes=count*size;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) return 0u;
    int32_t n=audio_file_lfs_read(context(file),(uint8_t *)file+4u,buffer,bytes);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if(n<0) return 0u;
    uint32_t result;
    __asm volatile("udiv %0, %1, %2" : "=r"(result) : "r"((uint32_t)n),"r"(size));
    return result;
}
int32_t audio_file_seek(void *file,int32_t offset,uint32_t whence) {
    if(whence>2u) return -1;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) return -1;
    int32_t status=audio_file_lfs_seek(context(file),(uint8_t *)file+4u,offset,whence);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    return status<0 ? -1 : 0;
}
int32_t audio_file_tell(void *file) {
    if(file==0) return -1;
    if(audio_file_mutex_acquire(audio_file_api_mutex,1000u)!=0) return -1;
    int32_t position=audio_file_lfs_tell(context(file),(uint8_t *)file+4u);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    return position<0 ? -1 : position;
}
