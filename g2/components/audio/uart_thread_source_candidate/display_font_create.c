/* Native LVGL FreeType font create 0x4b1c9c; children retain real contracts. */
#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected strlen 0x44a43c */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_lv_heap_alloc(uint32_t); /* 0x44f730 */
extern void audio_uart_lv_heap_free(void *); /* 0x44f758 */
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
extern uint32_t audio_uart_font_path_acquire(void *,const char *); /* 0x4b20d4 */
extern void audio_uart_font_path_release(void *,uint32_t); /* 0x4b21a0 */
extern void *audio_uart_font_cache_find(void *,const void *,uint32_t); /* 0x4d4dca */
extern void *audio_uart_font_cache_add(void *,const void *,uint32_t); /* 0x4d4f90 */
extern void audio_uart_font_cache_remove(void *,void *,uint32_t); /* 0x4d4e72 */
extern void *audio_uart_font_cache_info(void *); /* 0x4d5396 */
extern int32_t audio_uart_font_size_setup(void *,uint32_t); /* 0x4b202c */
extern void audio_uart_font_callbacks_attach(void *); /* 0x4b20aa */
extern int32_t audio_uart_font_face_load_scalable(void *,uint32_t,uint32_t); /* 0x526d54 */
extern int32_t audio_uart_font_face_select_size(void *,uint32_t); /* 0x526ca8 */
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* 0x5246f8 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char function[]="lv_freetype_font_create";
static const char assert_one[]="Asserted at expression: %s (%s)";
static const char assert_single[]="Asserted at expression: %s";
static const char null_pointer[]="NULL pointer";
static const char size_positive[]="size > 0";
static const char pathname_nonnull[]="pathname != NULL";
static const char pathname_nonempty[]="pathname_len > 0";
static const char cache_failure[]="cache node creating failed";
static const char out_of_memory[]="Out of memory";
static const char descriptor_nonnull[]="dsc != NULL";
static const char non_scalable[]="font is not scalable, selecting available size";
static const char size_error[]="FT_Set_Pixel_Sizes error(0x%x)";
static void font_assert_loop(uint32_t line,const char *expression,const char *reason) {
    if(reason!=0)
        audio_uart_lvgl_log(3u,source,line,function,assert_one,expression,reason);
    else
        audio_uart_lvgl_log(3u,source,line,function,assert_single,expression);
    for(;;) { /* authenticated native assertion loop */ }
}
void *audio_uart_font_create(const char *pathname,uint8_t render_mode,
                             uint32_t size,uint8_t style) {
    if(pathname==0) font_assert_loop(0x74u,pathname_nonnull,null_pointer);
    if(size==0u) font_assert_loop(0x75u,size_positive,0);
    if(g2_log_module_length(pathname)==0u)
        font_assert_loop(0x78u,pathname_nonempty,0);
    uint8_t *context=*(uint8_t **)(void *)(audio_uart_display_lv_state+0x1c0u);
    uint8_t key[32];
    audio_uart_buffer_zero(key,sizeof(key),0u);
    uint32_t path_key=audio_uart_font_path_acquire(context,pathname);
    *(uint32_t *)(void *)key=path_key;
    key[4u]=style;
    key[5u]=render_mode;
    void *cache=*(void **)(void *)(context+0x18u);
    void *node=audio_uart_font_cache_find(cache,key,0u);
    uint32_t newly_created=0u;
    if(node==0) {
        newly_created=1u;
        node=audio_uart_font_cache_add(cache,key,0u);
        if(node==0) {
            audio_uart_font_path_release(context,path_key);
            audio_uart_lvgl_log(3u,source,0x89u,function,cache_failure);
            return 0;
        }
    }
    uint8_t *descriptor=(uint8_t *)audio_uart_lv_heap_alloc(0x44u);
    if(descriptor==0) font_assert_loop(0x8fu,descriptor_nonnull,out_of_memory);
    *(uint32_t *)(void *)(descriptor+0x3cu)=path_key;
    descriptor[0x2du]=render_mode;
    *(uint32_t *)(void *)(descriptor+0x30u)=(uint32_t)(uintptr_t)context;
    *(uint32_t *)(void *)(descriptor+0x28u)=size;
    descriptor[0x2cu]=style;
    *(uint32_t *)(void *)descriptor=0x5f5f4654u; /* DAT_004b22b0 */
    uint8_t *cache_info=(uint8_t *)audio_uart_font_cache_info(node);
    *(uint32_t *)(void *)(descriptor+0x34u)=(uint32_t)(uintptr_t)cache_info;
    *(uint32_t *)(void *)(descriptor+0x38u)=(uint32_t)(uintptr_t)node;
    if(!newly_created&&audio_uart_font_size_setup(descriptor,
                 *(uint32_t *)(void *)(context+0x14u))==0) {
        audio_uart_font_cache_remove(cache,node,0u);
        audio_uart_font_path_release(context,path_key);
        audio_uart_lv_heap_free(descriptor);
        return 0;
    }
    audio_uart_font_callbacks_attach(descriptor);
    uint8_t *face=*(uint8_t **)(void *)(cache_info+0xcu);
    int32_t status;
    if((face[8u]&1u)!=0u)
        status=audio_uart_font_face_load_scalable(face,0u,size);
    else {
        audio_uart_lvgl_log(2u,source,0xa8u,function,non_scalable);
        status=audio_uart_font_face_select_size(face,0u);
    }
    if(status!=0) {
        audio_uart_lvgl_log(3u,source,0xacu,function,size_error,status);
        return 0;
    }
    *(uint32_t *)(void *)(descriptor+0x1cu)=(uint32_t)(uintptr_t)descriptor;
    descriptor[0x18u]&=0xfcu;
    uint8_t *size_metrics=*(uint8_t **)(void *)(face+0x58u);
    *(int32_t *)(void *)(descriptor+0x10u)=
        *(int32_t *)(void *)(size_metrics+0x20u)>>6u;
    *(int32_t *)(void *)(descriptor+0x14u)=
        -(*(int32_t *)(void *)(size_metrics+0x1cu)>>6u);
    uint32_t scale=*(uint32_t *)(void *)(size_metrics+0x14u);
    int32_t ascender=audio_uart_font_scale_metric(scale,
                         *(int16_t *)(void *)(face+0x52u));
    int32_t descender=audio_uart_font_scale_metric(scale,
                          *(int16_t *)(void *)(face+0x50u));
    descriptor[0x19u]=(uint8_t)(descender>>6u);
    int32_t height=ascender>>6u;
    if(height<1) height=1;
    descriptor[0x1au]=(uint8_t)height;
    return descriptor+4u;
}
