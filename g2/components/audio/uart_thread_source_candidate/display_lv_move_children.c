/* Native recursive child movement 0x44035e. */
#include <stdint.h>
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *,uint32_t);
void audio_uart_lv_obj_move_children_44035e(void *object,int32_t dx,int32_t dy,uint32_t skip_floating)
{
    uint32_t count=audio_uart_lv_child_count_44ddea(object);
    for(uint32_t i=0;i<count;i++){
        uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
        uint32_t *children=*(uint32_t **)(void *)spec;
        void *child=(void *)(uintptr_t)children[i];
        if((uint8_t)skip_floating && audio_uart_lv_obj_has_flag_43e0e0(child,0x40000u))continue;
        int32_t *r=(int32_t *)((uint8_t *)child+0x14u);
        r[0]=(int32_t)((uint32_t)r[0]+(uint32_t)dx);
        r[1]=(int32_t)((uint32_t)r[1]+(uint32_t)dy);
        r[2]=(int32_t)((uint32_t)r[2]+(uint32_t)dx);
        r[3]=(int32_t)((uint32_t)r[3]+(uint32_t)dy);
        audio_uart_lv_obj_move_children_44035e(child,dx,dy,0u);
    }
}
