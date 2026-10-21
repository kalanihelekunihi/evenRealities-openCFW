/* Native lv_obj_allocate_spec_attr 0x43e1fa. Full allocation and original
 * assertion paths; existing spec attributes are left intact. */
#include <stdint.h>
extern void *audio_uart_lv_heap_alloc(uint32_t); /* selected zeroed 0x44f730 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c";
void audio_uart_lv_obj_setup_layer_43e1fa(void *object) {
    if(object==0) {
        audio_uart_lvgl_log(3u,path,0x178u,"lv_obj_allocate_spec_attr",
                            "Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *obj=(uint8_t *)object;
    void *existing=*(void **)(void *)(obj+8u);
    if(existing!=0)return;
    uint8_t *layer=(uint8_t *)audio_uart_lv_heap_alloc(0x34u);
    *(void **)(void *)(obj+8u)=layer;
    if(layer==0) {
        audio_uart_lvgl_log(3u,path,0x17cu,"lv_obj_allocate_spec_attr",
                            "Asserted at expression: %s (%s)","obj->spec_attr != NULL","Out of memory");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint16_t bits;__builtin_memcpy(&bits,layer+0x32u,2u);
    bits|=0x03c3u;__builtin_memcpy(layer+0x32u,&bits,2u);
}
