/* Full native4c81a2..4c8204, literal pool excluded. get_decoder_data.
 * Unselected pending native comparisons. */
#include <stdint.h>
extern void *audio_uart_lv_heap_alloc(uint32_t); /* selected zeroed44f730 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *descriptor)
{
    volatile uint32_t *dsc=descriptor;
    void *data=(void *)(uintptr_t)dsc[18];
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if(data==0) {
        data=audio_uart_lv_heap_alloc(68u);
        if(data==0) {
            audio_uart_lvgl_log(3u,source,536u,"get_decoder_data","Asserted at expression: %s (%s)","data != NULL","Out of memory");
            for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if(data==0) {
            audio_uart_lvgl_log(3u,source,538u,"get_decoder_data","Out of memory");
            return 0;
        }
        dsc[18]=(uint32_t)(uintptr_t)data;
    }
    return data;
}
