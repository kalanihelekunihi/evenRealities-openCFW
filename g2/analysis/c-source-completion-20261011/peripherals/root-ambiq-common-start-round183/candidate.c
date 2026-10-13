#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern int32_t audio_uart_ambiq_color_format_dst_4b064e(uint32_t);
extern uint32_t audio_uart_ambiq_context_lock_4b07de(void *);
extern int32_t audio_uart_nema_power_control_51419a(uint32_t,uint32_t);
extern void *audio_uart_nema_cl_get_bound_5144fa(void);
extern void audio_uart_nema_cl_rewind_514384(void *);
extern void audio_uart_nema_cl_bind_sectored_5143d4(void *,uint32_t);
extern int32_t audio_uart_nema_last_cl_id_51418e(void);
extern uint32_t audio_uart_nema_last_submission_id_514194(void);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_ambiq_blend_clear_4b075e(void *);
extern uint32_t audio_uart_ambiq_context_unlock_4b0886(void *);
extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,uint32_t,int32_t,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_uart_ambiq_clip_change_4b077e(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Native4b092a..4b0b5a; unit cached once, all source/header reads volatile.
 * Null buffer is dereferenced before the later validation, as in native. */
uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *buffer,const void *raw_clip,uint32_t extend) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_common_start";
    volatile uint32_t *b=buffer;
    uint8_t *unit=audio_uart_ambiq_default_unit_4c791a();
    uint32_t bounds[4],clip[4];
    audio_uart_lv_memzero_48949c(bounds,16u);
    bounds[2]=(uint16_t)b[1]-1u;
    bounds[3]=(b[1]>>16)-1u;
    if(!raw_clip)raw_clip=bounds;
    if(!audio_uart_lv_area_intersect_450bcc((int32_t *)clip,raw_clip,(const int32_t *)bounds))return 0u;
    if((int32_t)(clip[2]-clip[0])<1||(int32_t)(clip[3]-clip[1])<1)return 0u;
    if(!buffer||!b[4]||(int32_t)(uint16_t)b[1]<1||(int32_t)(b[1]>>16)<1) {
        audio_uart_lvgl_log(3u,source,332u,name,"Invalid buffer setting!");return 0u;
    }
    int32_t format=audio_uart_ambiq_color_format_dst_4b064e((uint8_t)(b[0]>>8));
    uint32_t data=b[4];
    if(format==-1&&(uint8_t)extend==1u) {
        if((uint8_t)(b[0]>>8)==20u)format=4;
        else if((uint32_t)((uint8_t)(b[0]>>8))-7u<4u) {
            uint32_t count;
            switch((uint8_t)(b[0]>>8)) {
            case 7:count=2u;format=11;break;
            case 8:count=4u;format=49;break;
            case 9:count=16u;format=53;break;
            default:count=256u;format=9;break;
            }
            data+=count*4u;
        }
    }
    if(format==-1) {
        audio_uart_lvgl_log(3u,source,377u,name,"Unsupported layer color format!");return 0u;
    }
    audio_uart_ambiq_context_lock_4b07de(unit);
    int32_t power=audio_uart_nema_power_control_51419a(0u,1u);
    if(power) {
        audio_uart_lvgl_log(3u,source,385u,name,"Power control failed: %d\r\n",power);return 0u;
    }
    void *bound=audio_uart_nema_cl_get_bound_5144fa();
    if(!bound) {
        audio_uart_nema_cl_rewind_514384(unit+144u);
        audio_uart_nema_cl_bind_sectored_5143d4(unit+144u,100u);
    } else if(bound!=unit+144u) {
        audio_uart_ambiq_context_unlock_4b0886(unit);
        audio_uart_lvgl_log(3u,source,399u,name,"Unexpected command list in the context!\r\n");return 0u;
    }
    if(audio_uart_nema_last_cl_id_51418e()<0&&audio_uart_nema_last_submission_id_514194()==0u) {
        audio_uart_lv_basic_box_clear_454746(unit+88u,0u,28u);
        audio_uart_lv_basic_box_clear_454746(unit+116u,0u,16u);
        audio_uart_ambiq_blend_clear_4b075e(unit);
    }
    volatile uint32_t *old=(void *)(unit+88u);
    if(b[4]!=old[4]||(uint16_t)b[1]!=(uint16_t)old[1]||(b[1]>>16)!=(old[1]>>16)
       ||(uint8_t)(b[0]>>8)!=(uint8_t)(old[0]>>8)||(uint16_t)b[2]!=(uint16_t)old[2]) {
        uint32_t stride=(uint16_t)b[2],height=b[1]>>16,width=(uint16_t)b[1];
        audio_uart_nema_bind_tex_4b1298(0u,data,width,height,format,stride,0u);
        audio_uart_checksum_copy(unit+88u,buffer,28u);
    }
    audio_uart_ambiq_clip_change_4b077e(unit,clip,0u);
    return 1u;
}
