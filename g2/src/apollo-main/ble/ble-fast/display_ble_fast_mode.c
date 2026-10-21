/* Native APP_ConnectParamESSSetFastMode 0x478160. */
#include <stdint.h>
extern volatile uint8_t audio_ble_fast_mode_throttle_enabled; /* RAM 0x20074f90 */
extern uint32_t audio_ble_fast_mode_last_reject_tick; /* RAM 0x20074340 */
extern void audio_ble_connect_param_request(uint8_t); /* native callback ROM 0x47761d */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected osKernelGetTickCount 0x4490cc */
extern void audio_event_loop_remove_delayed(void (*)(void)); /* native 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* native 0x47697e */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.param";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_connect_params.c";
static const char function[]="APP_ConnectParamESSSetFastMode";
static const char message[]="Connection param update was recently rejected, skip immediate retry. Elapsed: %d ms, remaining: %d ms";
static const char short_message[]="[ble.param]Connection param update was recently rejected, skip immediate retry. Elapsed: %d ms, remaining: %d ms";
void audio_ble_set_fast_mode(void) {
    if(audio_ble_fast_mode_throttle_enabled!=0u&&audio_ble_fast_mode_last_reject_tick!=0u) {
        uint32_t elapsed=g2_flashdb_candidate_tick()-audio_ble_fast_mode_last_reject_tick;
        if(elapsed<30000u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(4u,module,path,function,488u,message,elapsed,30000u-elapsed);
            if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x10800000u,short_message,short_message,elapsed,30000u-elapsed);
            return;
        }
    }
    audio_event_loop_remove_delayed((void (*)(void))audio_ble_connect_param_request);
    audio_event_loop_push_delayed((void (*)(void))audio_ble_connect_param_request,163u,0u);
}
