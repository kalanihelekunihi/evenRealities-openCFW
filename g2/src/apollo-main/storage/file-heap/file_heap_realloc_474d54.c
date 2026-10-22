/* Mutex-owned TLSF realloc wrapper, stock Apollo 0x474d54. */
#include <stdint.h>

extern void *g2_codec_heap_mutex;
extern void *g2_codec_heap_pool;
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern void *g2_tlsf_reallocate_4d0868(void *, void *, uint32_t);
extern void g2_file_heap_error_log(const char *);
extern void g2_file_close_error(const char *, const char *, uint32_t);

/* Stock 0x474D54 (file_heap_reallocate) */
void *audio_file_heap_realloc(void *old_buffer, uint32_t bytes) {
    void *result = 0;
    if (audio_file_mutex_acquire(g2_codec_heap_mutex, 1000u) == 0) {
        result = g2_tlsf_reallocate_4d0868(g2_codec_heap_pool, old_buffer, bytes);
        (void)audio_file_mutex_release(g2_codec_heap_mutex);
    } else {
        g2_file_heap_error_log((const char *)(uintptr_t)0x764730u);
        g2_file_close_error((const char *)(uintptr_t)0x474e40u,
                            (const char *)(uintptr_t)0x6fc7c4u, 0x449u);
    }
    return result;
}
