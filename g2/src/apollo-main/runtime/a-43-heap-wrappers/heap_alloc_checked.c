/* Checked heap allocate/free pair, native 0x51008a..0x51009f (no literal pool).
 * Stock source path unknown: the pair sits between the LVGL lv_tileview.c
 * code and platform\service\callback_mgr\callback_manager.c and has no log
 * strings. Its only callers are in the onboarding main page create code
 * (0x4ab838/0x4ab846 allocate two count*4 arrays, 0x4aba3c/0x4aba42 free
 * them). The shape (abort on NULL, plain free) is also that of an IAR
 * operator new[]/delete[] pair; no C++ evidence was found, so it is kept as C. */
#include <stdint.h>

extern void *codec_allocate(uint32_t bytes);  /* file_heap_allocate 0x474cd2 */
extern void audio_file_heap_free(void *buffer); /* file_heap_free 0x474d16 */
extern void g2_main_formatter_abort(void);    /* 0x541b74: exit(1) via the semihost SYS_EXIT loop */

void *heap_alloc_or_abort_51008a(uint32_t bytes)
{
    void *block = codec_allocate(bytes);
    if (block == 0)
        g2_main_formatter_abort();
    return block;
}

/* Stock is a bare tail call (b.w), with no NULL check. */
void heap_free_51009c(void *block)
{
    audio_file_heap_free(block);
}
