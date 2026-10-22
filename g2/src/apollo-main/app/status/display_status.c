/* RING_SendGlassesStatusEvt native 0x47243a. */
#include <stdint.h>
extern uint32_t audio_uart_case_status(void); /* 0x4acad0 */
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint32_t semantic_get_aid_enabled(void);
extern uint32_t audio_uart_lcd_status(void); /* 0x49eb8e */
extern int32_t audio_uart_ring_task_msg_send(uint32_t,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ring.proto";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_service.c";
static const char fn[]="RING_SendGlassesStatusEvt";
static const char extended[]="glasses status send to ring: in case: %d, wear status: %d, imu status: %d, lcd status: %d, status: 0x%02X 0x%02X";
static const char compact[]="[ring.proto]glasses status send to ring: in case: %d, wear status: %d, imu status: %d, lcd status: %d, status: 0x%02X 0x%02X";
/* Stock 0x47243A (RING_SendGlassesStatusEvt) */
int32_t audio_uart_display_housekeep(void) {
    uint8_t in_case=(uint8_t)audio_uart_case_status();
    uint8_t wear=(uint8_t)audio_log_wake_allowed();
    uint8_t imu=(uint8_t)semantic_get_aid_enabled();
    uint8_t lcd=(uint8_t)audio_uart_lcd_status();
    uint8_t status[2]={0u,0u};
    status[0]=(imu==0u||lcd==2u)?1u:0u;
    if(in_case==1u) status[0]=0u;
    status[1]=(uint8_t)(in_case!=1u&&wear==1u);
    if(audio_log_flags()&2u)
        audio_log_extended(3u,module,source,fn,0x187u,extended,
                           in_case,lcd,imu,wear,status[0],status[1]);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0xd800000u,compact,compact,
                                    in_case,lcd,imu,wear,status[0],status[1]);
    return (int8_t)audio_uart_ring_task_msg_send(0x400u,status,2u);
}
