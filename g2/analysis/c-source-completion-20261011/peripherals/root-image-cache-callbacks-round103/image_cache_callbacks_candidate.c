#include <stdint.h>
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lv_heap_free(void *);
/* Full native4d4b32..4d4b94 and duplicated4d4c3a..4d4c9c. */
static int32_t source_order(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{
    ak=(uint8_t)ak; bk=(uint8_t)bk;
    if(ak!=bk) return ak>bk ? 1 : -1;
    if(ak==1u) {
        int32_t cmp=audio_uart_lv_string_compare_4547be(
            (const char *)(uintptr_t)a,(const char *)(uintptr_t)b);
        return cmp==0 ? 0 : cmp>0 ? 1 : -1;
    }
    if(ak==0u) return a==b ? 0 : a>b ? 1 : -1;
    return 0;
}
int32_t audio_uart_lv_image_source_compare_4d4b32(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{ return source_order(a,ak,b,bk); }
int32_t audio_uart_lv_image_header_source_compare_4d4c3a(uint32_t a,uint32_t ak,uint32_t b,uint32_t bk)
{ return source_order(a,ak,b,bk); }
/* Full native4d4b94..4d4ba4: image node kind at8,source at4. */
int32_t audio_uart_lv_image_cache_compare_4d4b94(const void *a,const void *b)
{
    const volatile uint8_t *x=a,*y=b;
    return audio_uart_lv_image_source_compare_4d4b32(
        *(const volatile uint32_t *)(const void *)(x+4),x[8],
        *(const volatile uint32_t *)(const void *)(y+4),y[8]);
}
/* Full native4d4c9c..4d4cac: header node kind at4,source at0. */
int32_t audio_uart_lv_image_header_cache_compare_4d4c9c(const void *a,const void *b)
{
    const volatile uint8_t *x=a,*y=b;
    return audio_uart_lv_image_header_source_compare_4d4c3a(
        *(const volatile uint32_t *)(const void *)x,x[4],
        *(const volatile uint32_t *)(const void *)y,y[4]);
}
/* Full native4d4ba4..4d4bca. Saved draw owner and fresh key after child. */
void audio_uart_lv_image_cache_free_4d4ba4(void *entry)
{
    volatile uint8_t *p=entry;
    void *draw=(void *)(uintptr_t)*(volatile uint32_t *)(void *)(p+12);
    if(audio_uart_lv_draw_buf_has_flag_48b73c(draw,16u)!=0u)
        audio_uart_font_bitmap_release(draw);
    if(p[8]==1u) audio_uart_lv_heap_free(
        (void *)(uintptr_t)*(volatile uint32_t *)(void *)(p+4));
}
/* Full native4d4cac..4d4cbc. */
void audio_uart_lv_image_header_cache_free_4d4cac(void *entry)
{
    volatile uint8_t *p=entry;
    if(p[4]==1u) audio_uart_lv_heap_free(
        (void *)(uintptr_t)*(volatile uint32_t *)(void *)p);
}
