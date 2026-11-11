/* Mutex-owned file/TLSF heap free, stock 0x474d16. */
#include <stdint.h>
extern int32_t audio_file_mutex_acquire(void *mutex,uint32_t ticks);
extern int32_t audio_file_mutex_release(void *mutex);
extern void g2_file_pool_free(void *pool,void *buffer); /* stock 0x4d0808 */
extern void g2_file_heap_error_log(const char *message); /* 0x4733ee */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line); /* 0x4d09b4 */
/* Sim-test fix (2026-10-26): stock cells RAM 0x200748f8 (mutex) and
 * 0x20074abc (TLSF pool) are the same cells codec_allocate (stock 0x474cd2,
 * codec-heap-allocate.c) and file_heap_realloc_474d54.c reach through
 * g2_codec_heap_mutex/g2_codec_heap_pool, written by
 * file_redirect_init_474d9c.c. Absolute stock RAM addresses are unmapped in
 * our link (DTCM free gap), so free always failed the mutex and asserted
 * (Renode: lfs_deinit -> lfs_free -> here, line 1086). */
extern void *g2_codec_heap_mutex;
extern void *g2_codec_heap_pool;
void audio_file_heap_free(void *buffer) {
    if(audio_file_mutex_acquire(g2_codec_heap_mutex,1000u)==0) {
        g2_file_pool_free(g2_codec_heap_pool,buffer);
        (void)audio_file_mutex_release(g2_codec_heap_mutex);
    } else {
        g2_file_heap_error_log("get free semaphore failed.\r\n" /* stock 0x764710 */);
        g2_file_close_error("0" /* stock 0x474e40 */,
                            "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\redirect.c" /* stock 0x6fc7c4 */,1086u);
    }
}
/* Stock file_heap_free entry: single implementation. */
__typeof__(audio_file_heap_free) file_heap_free __attribute__((alias("audio_file_heap_free")));
