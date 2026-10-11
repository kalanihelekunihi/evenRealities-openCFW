/* Native FreeType face-id pathname retain/release 0x4b20d4/0x4b21a0. */
#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected strlen */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_lv_list_first(void *); /* 0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* 0x482cf0 */
extern void audio_uart_lv_list_remove(void *,void *); /* 0x482c0e */
extern void *audio_uart_font_path_node_append(void *); /* 0x482bca */
extern int32_t audio_uart_font_path_compare(const char *,const char *); /* 0x46cacc */
extern char *audio_uart_font_path_duplicate(const char *); /* 0x4547c6 */
extern void audio_uart_lv_free(void *); /* selected 0x44f758 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype.c";
static const char req_fn[]="lv_freetype_req_face_id";
static const char drop_fn[]="lv_freetype_drop_face_id";
static const char assert_single[]="Asserted at expression: %s";
static const char assert_reason[]="Asserted at expression: %s (%s)";
static const char positive[]="len > 0";
static const char node_nonnull[]="node != NULL";
static const char path_nonnull[]="node->pathname != NULL";
static const char false_expression[]="false";
static const char not_found[]="face_id not found";
static const char out_of_memory[]="Out of memory";
static const char null_pointer[]="NULL pointer";
static void path_assert(uint32_t line,const char *function,
                        const char *expression,const char *reason) {
    if(reason!=0)
        audio_uart_lvgl_log(3u,source,line,function,assert_reason,expression,reason);
    else
        audio_uart_lvgl_log(3u,source,line,function,assert_single,expression);
    for(;;) { /* authenticated native assertion loop */ }
}
uint32_t audio_uart_font_path_acquire(void *context,const char *pathname) {
    if(g2_log_module_length(pathname)==0u)
        path_assert(0x129u,req_fn,positive,0);
    uint8_t *list=(uint8_t *)context+4u;
    for(uint32_t *node=(uint32_t *)audio_uart_lv_list_first(list);node!=0;
        node=(uint32_t *)audio_uart_lv_list_next(list,node)) {
        if(audio_uart_font_path_compare((const char *)(uintptr_t)node[0],pathname)==0) {
            node[1]+=1u;
            return node[0];
        }
    }
    uint32_t *node=(uint32_t *)audio_uart_font_path_node_append(list);
    if(node==0) path_assert(0x139u,req_fn,node_nonnull,out_of_memory);
    node[0]=(uint32_t)(uintptr_t)audio_uart_font_path_duplicate(pathname);
    if(node[0]==0u) path_assert(0x148u,req_fn,path_nonnull,null_pointer);
    node[1]=1u;
    return node[0];
}
void audio_uart_font_path_release(void *context,uint32_t path_key) {
    uint8_t *list=(uint8_t *)context+4u;
    for(uint32_t *node=(uint32_t *)audio_uart_lv_list_first(list);;
        node=(uint32_t *)audio_uart_lv_list_next(list,node)) {
        if(node==0) path_assert(0x163u,drop_fn,false_expression,not_found);
        if(node[0]!=path_key) continue;
        node[1]-=1u;
        if(node[1]==0u) {
            audio_uart_lv_list_remove(list,node);
            audio_uart_lv_free((void *)(uintptr_t)node[0]);
            audio_uart_lv_free(node);
        }
        return;
    }
}
