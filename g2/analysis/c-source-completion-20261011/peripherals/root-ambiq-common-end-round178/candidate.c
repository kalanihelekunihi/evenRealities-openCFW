#include <stdint.h>
extern volatile uint32_t audio_uart_ambiq_unit_cell[];
extern uint32_t audio_uart_nema_cl_submit_514cf2(void *);
extern uint32_t audio_uart_nema_cl_wait_514d00(void *);
extern void audio_uart_nema_cl_unbind_5144ba(void);
extern int32_t audio_uart_nema_power_control_51419a(uint32_t,uint32_t);
extern void audio_uart_ambiq_context_unlock_4b0886(void *);
extern uint32_t audio_uart_nema_get_error_4b128a(void);
extern uint32_t audio_uart_nema_vg_get_error_51564c(void);
extern const char *audio_uart_nema_error_interpret_4b0594(uint32_t);
extern const char *audio_uart_nema_vg_error_interpret_4b0584(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Native4c791a..4c7920; mutable default unit cell read once per invocation. */
void *audio_uart_ambiq_default_unit_4c791a(void) {
    return (void *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
}
/* Native4b0c8a..4b0d38. Native power failure returns0 before unlock/errors. */
uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t sync) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
    static const char name[]="lv_draw_ambiq_common_end";
    uint8_t *unit=audio_uart_ambiq_default_unit_4c791a();
    if((uint8_t)sync) {
        audio_uart_nema_cl_submit_514cf2(unit+144u);
        audio_uart_nema_cl_wait_514d00(unit+144u);
        audio_uart_nema_cl_unbind_5144ba();
        int32_t power=audio_uart_nema_power_control_51419a(2u,1u);
        if(power) {
            audio_uart_lvgl_log(3u,source,538u,name,"Power control failed: %d\r\n",power);
            return 0u;
        }
    }
    audio_uart_ambiq_context_unlock_4b0886(unit);
    uint32_t error=audio_uart_nema_get_error_4b128a();
    if(error) {
        const char *text=audio_uart_nema_error_interpret_4b0594(error);
        audio_uart_lvgl_log(3u,source,555u,name,"NemaGFX error 0x%lx, %s\r\n",error,text);
    }
    error=audio_uart_nema_vg_get_error_51564c();
    if(error) {
        const char *text=audio_uart_nema_vg_error_interpret_4b0584(error);
        audio_uart_lvgl_log(3u,source,559u,name,"NemaVG error: 0x%lx, %s\r\n",error,text);
    }
    return 1u;
}
