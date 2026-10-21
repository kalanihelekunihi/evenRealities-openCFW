/* Native lv_obj_get_screen 0x44dbc4 and lv_obj_get_display 0x44dc0a.
 * Display registry is live LVGL RAM at 0x2006f54c. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* 0x2006f548 */
extern void *audio_uart_lv_list_first(void *); /* 0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* 0x482cf0 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
static const char asserted[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char null_pointer[]="NULL pointer";
static const char get_screen[]="lv_obj_get_screen";
static const char get_display[]="lv_obj_get_display";
static const char no_screen[]="No screen found";
static void invalid_object(uint32_t line,const char *function) {
    audio_uart_lvgl_log(3u,source_path,line,function,asserted,expression,null_pointer);
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void *audio_uart_lv_object_screen(void *object) {
    if(object==0) invalid_object(292u,get_screen);
    uint8_t *root=(uint8_t *)object;
    while(*(void **)(void *)(root+4u)!=0) root=*(uint8_t **)(void *)(root+4u);
    return root;
}
void *audio_uart_lv_display_for_object(void *object) {
    if(object==0) invalid_object(307u,get_display);
    uint8_t *screen=(uint8_t *)object;
    if(*(void **)(void *)(screen+4u)!=0) screen=(uint8_t *)audio_uart_lv_object_screen(screen);
    void *list=audio_uart_display_lv_root+4u;
    for(uint8_t *display=(uint8_t *)audio_uart_lv_list_first(list);
        display!=0;display=(uint8_t *)audio_uart_lv_list_next(list,display)) {
        uint32_t count=*(uint32_t *)(void *)(display+0x2d4u);
        uint8_t **screens=*(uint8_t ***)(void *)(display+0x2b8u);
        for(uint32_t i=0;i<count;i++) if(screens[i]==screen) return display;
    }
    audio_uart_lvgl_log(2u,source_path,323u,get_display,no_screen);
    return 0;
}
