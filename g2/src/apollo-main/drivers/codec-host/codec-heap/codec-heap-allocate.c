#include <stdint.h>

/* Native 0x474cd2..0x474d15. The mutex and TLSF pool cells at
 * 0x200748f8 and 0x20074abc are product RAM contracts. */
extern void *g2_codec_heap_mutex;
extern void *g2_codec_heap_pool;
extern int32_t audio_file_mutex_acquire(void *mutex, uint32_t ticks);
extern int32_t audio_file_mutex_release(void *mutex);
extern void *g2_file_pool_allocate(void *pool, uint32_t bytes); /* 0x4d0722 */
extern void g2_file_heap_error_log(const char *message);       /* 0x4733ee */
extern void g2_file_close_error(const char *message,
                                const char *file, uint32_t line); /* 0x4d09b4 */

void *codec_allocate(uint32_t bytes) {
    void *allocated = 0;
    if (audio_file_mutex_acquire(g2_codec_heap_mutex, 1000u) == 0) {
        allocated = g2_file_pool_allocate(g2_codec_heap_pool, bytes);
        (void)audio_file_mutex_release(g2_codec_heap_mutex);
    } else {
        g2_file_heap_error_log((const char *)(uintptr_t)0x7646f0u);
        g2_file_close_error((const char *)(uintptr_t)0x474e40u,
                            (const char *)(uintptr_t)0x6fc7c4u, 1074u);
    }
    return allocated;
}
