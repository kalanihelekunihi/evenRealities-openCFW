/* Mutex-owned file/TLSF heap free, stock 0x474d16. */
#include <stdint.h>
extern int32_t audio_file_mutex_acquire(void *mutex,uint32_t ticks);
extern int32_t audio_file_mutex_release(void *mutex);
extern void g2_file_pool_free(void *pool,void *buffer); /* stock 0x4d0808 */
extern void g2_file_heap_error_log(const char *message); /* 0x4733ee */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line); /* 0x4d09b4 */
void audio_file_heap_free(void *buffer) {
    volatile void **mutex_cell=(volatile void **)(uintptr_t)0x200748f8u;
    if(audio_file_mutex_acquire((void *)*mutex_cell,1000u)==0) {
        void *pool=*(void *volatile *)(uintptr_t)0x20074abcu;
        g2_file_pool_free(pool,buffer);
        (void)audio_file_mutex_release((void *)*mutex_cell);
    } else {
        g2_file_heap_error_log((const char *)(uintptr_t)0x764710u);
        g2_file_close_error((const char *)(uintptr_t)0x474e40u,
                            (const char *)(uintptr_t)0x6fc7c4u,1086u);
    }
}
