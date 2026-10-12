/* Native LVGL cache-entry accessors 0x4d5312 and 0x4d5396. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_entry.c";
static const char assertion[]="Asserted at expression: %s (%s)";
static const char expression[]="entry != NULL";
static const char reason[]="NULL pointer";
static const char ref_function[]="lv_cache_entry_get_ref";
static const char data_function[]="lv_cache_entry_get_data";
static const char inc_function[]="lv_cache_entry_inc_ref";

uint32_t audio_uart_font_cache_has_owner(void *entry) {
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x4au,ref_function,assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    return *(uint32_t *)(void *)((uint8_t *)entry+4u);
}

void *audio_uart_font_cache_info(void *entry) {
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x67u,data_function,assertion,expression,reason);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t offset=*(uint32_t *)(void *)((uint8_t *)entry+8u);
    return (void *)((uintptr_t)entry-offset);
}

void audio_uart_font_cache_retain(void *entry) { /* native 0x4d5278 */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x3au,inc_function,assertion,expression,reason);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    ++*(uint32_t *)(void *)((uint8_t *)entry+4u);
}

void *audio_uart_font_cache_acquire_data(void *entry) { /* native 0x4d53c6 */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x6du,"lv_cache_entry_acquire_data",
                            assertion,expression,reason);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    audio_uart_font_cache_retain(entry);
    return audio_uart_font_cache_info(entry);
}

uint32_t audio_uart_font_cache_is_invalid(void *entry) { /* native 0x4d536a */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x61u,"lv_cache_entry_is_invalid",
                            assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    return ((uint8_t *)entry)[0x0cu];
}

void audio_uart_font_cache_decrement(void *entry) { /* native 0x4d52b2 */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x40u,"lv_cache_entry_dec_ref",
                            assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    int32_t *ref=(int32_t *)(void *)((uint8_t *)entry+4u);
    --*ref;
    if(*ref<0) {
        audio_uart_lvgl_log(2u,source,0x43u,"lv_cache_entry_dec_ref",
                            "ref_cnt(%u) < 0",(uint32_t)*ref);
        *ref=0;
    }
}

void audio_uart_font_cache_release_data(void *entry) { /* native 0x4d5400 */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x77u,"lv_cache_entry_release_data",
                            assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint32_t ref=audio_uart_font_cache_has_owner(entry);
    if(ref==0u)
        audio_uart_lvgl_log(3u,source,0x79u,"lv_cache_entry_release_data",
                            "ref_cnt(%u) == 0",ref);
    else audio_uart_font_cache_decrement(entry);
}

void audio_uart_font_cache_set_invalid(void *entry,uint8_t invalid) { /* native 0x4d533e */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0x5bu,"lv_cache_entry_set_invalid",
                            assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    ((uint8_t *)entry)[0x0cu]=invalid;
}

extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
void audio_uart_font_cache_entry_delete(void *entry) { /* native 0x4d54da */
    if(entry==0) {
        audio_uart_lvgl_log(3u,source,0xb1u,"lv_cache_entry_delete",
                            assertion,expression,reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    void *data=audio_uart_font_cache_info(entry);
    audio_uart_lv_heap_free(data);
}

void *audio_uart_font_cache_entry_at(void *data,uint32_t offset) { /* native 0x4d5452 */
    if(data==0) {
        audio_uart_lvgl_log(3u,source,0x82u,"lv_cache_entry_get_entry",
                            assertion,"data != NULL",reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    return (uint8_t *)data+offset;
}

void audio_uart_font_cache_entry_init(void *entry,void *data,uint32_t offset) { /* 0x4d547e */
    if(entry==0 || data==0) {
        audio_uart_lvgl_log(3u,source,entry==0?0xa6u:0xa7u,
            "lv_cache_entry_init",assertion,
            entry==0?expression:"cache != NULL",reason);
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint8_t *e=(uint8_t *)entry;
    *(uint32_t *)(void *)e=(uint32_t)(uintptr_t)data;
    *(uint32_t *)(void *)(e+4u)=0u;
    *(uint32_t *)(void *)(e+8u)=offset;
    e[0x0cu]=0u;
}
