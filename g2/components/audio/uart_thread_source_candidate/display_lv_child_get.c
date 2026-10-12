/* Native lv_obj_get_child 0x44dce2, including negative indexing and assertion. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
static const char function[]="lv_obj_get_child";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
void *audio_uart_lv_child_get_44dce2(void *object,int32_t index)
{
    if(!object){
        audio_uart_lvgl_log(3u,source,0x151u,function,format,expression,message);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
    if(!spec)return 0;
    uint32_t count=*(uint16_t *)(void *)(spec+0x30u);
    uint32_t slot=(uint32_t)index;
    if(index<0){slot+=count;if((int32_t)slot<0)return 0;}
    if(slot>=count)return 0;
    uint32_t *children=*(uint32_t **)(void *)spec;
    return (void *)(uintptr_t)children[slot];
}
