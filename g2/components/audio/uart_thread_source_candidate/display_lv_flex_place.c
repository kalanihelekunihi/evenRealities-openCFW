/* Native LVGL flex place_content 0x48c6d8, pinned LVGL v9.3 cases. */
#include <stdint.h>
void audio_uart_lv_place_content_48c6d8(uint32_t placement,int32_t max_size,
                                        int32_t content_size,uint32_t item_count,
                                        int32_t *start,int32_t *gap)
{
    uint8_t place=(uint8_t)placement;
    if(item_count<2u && (place==3u || place==4u))place=2u;
    switch(place){
    case 1u: *gap=0;*start+=max_size-content_size;return;
    case 2u: *gap=0;*start+=(max_size-content_size)/2;return;
    case 3u: *gap=(max_size-content_size)/(int32_t)(item_count+1u);*start+=*gap;return;
    case 4u: *gap+=(max_size-content_size)/(int32_t)item_count;*start+=*gap/2;return;
    case 5u: if(item_count>1u)*gap=(max_size-content_size)/(int32_t)(item_count-1u);return;
    default: *gap=0;return;
    }
}
