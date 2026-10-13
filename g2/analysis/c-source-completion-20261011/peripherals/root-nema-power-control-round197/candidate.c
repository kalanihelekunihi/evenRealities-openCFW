#include <stdint.h>
extern uint32_t audio_uart_nema_power_status_47f90c(uint32_t,uint8_t *);
extern uint32_t audio_power_peripheral_on(uint32_t);
extern uint32_t audio_power_peripheral_off(uint32_t);
extern uint32_t audio_uart_nema_get_error_4b128a(void);
extern uint32_t audio_uart_nema_vg_get_error_51564c(void);
extern void audio_uart_nema_reset_last_submission_514184(void);
extern void audio_uart_nema_gpu_reinit_4b11b0(void);
extern void audio_uart_nema_vg_reinit_5224b6(void);
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern volatile uint32_t audio_uart_nema_vg_context_cell;
/* Native51419a..514238. Preserve low-byte policy and ordered error consumption. */
int32_t audio_uart_nema_power_control_51419a(uint32_t state,uint32_t reinit) {
    uint8_t powered;
    uint32_t result=audio_uart_nema_power_status_47f90c(20u,&powered);
    if(result) return result;
    state=(uint8_t)state;
    if(state==0u) {
        if(powered) return 0u;
        result=audio_power_peripheral_on(20u);
        if(result || (uint8_t)reinit==0u) return result;
        (void)audio_uart_nema_get_error_4b128a();
        audio_uart_nema_reset_last_submission_514184();
        audio_uart_nema_gpu_reinit_4b11b0();
        if(audio_uart_nema_get_error_4b128a()) return 1u;
        if(audio_uart_nema_vg_context_cell!=0u) {
            (void)audio_uart_nema_vg_get_error_51564c();
            audio_uart_nema_vg_reinit_5224b6();
            if(audio_uart_nema_vg_get_error_51564c()) return 1u;
        }
        return 0u;
    }
    if(state<=2u) {
        if(!powered) return 0u;
        if(audio_uart_nema_reg_read_51403c(252u)) return 3u;
        return audio_power_peripheral_off(20u);
    }
    return 7u;
}
