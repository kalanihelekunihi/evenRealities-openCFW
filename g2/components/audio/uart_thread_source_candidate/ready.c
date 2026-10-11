/* SyncModuleInit native 0x45e8d0. ROM role-specific listener order and
 * queue attributes are retained; callback bodies remain independent code. */
#include <stdint.h>
extern uint8_t audio_uart_role_get(void); /* 0x45a578 */
extern void *audio_uart_module_new(uint32_t); /* 0x4917d2 */
extern void audio_uart_module_listener(void *,uint32_t,void *); /* 0x491962 */
extern uint32_t audio_uart_master_prepare(void); /* 0x45d1ec */
extern uint32_t audio_uart_poll_thread_start(void); /* 0x49137a */
extern uint32_t audio_uart_sync_timer_start(void); /* 0x45d34c */
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* 0x449a32 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void *g2_uart_tinyframe; /* RAM0x200749c4 */
extern void *g2_uart_send_queue; /* RAM0x200749cc */
extern uint8_t g2_uart_send_queue_control[0x50]; /* RAM0x20072df8 */
extern uint8_t g2_uart_send_queue_storage[0x258]; /* RAM0x2006e860 */
extern uint32_t audio_uart_listener_master0(void *,const void *,uint32_t,uint32_t); /* 0x45b14c */
extern uint32_t audio_uart_listener_common1(void *,const void *,uint32_t,uint32_t); /* 0x45b588 */
extern uint32_t audio_uart_listener_common4(void *,const void *,uint32_t,uint32_t); /* 0x45b6e4 */
extern uint32_t audio_uart_listener_slave2(void *,const void *,uint32_t,uint32_t); /* 0x45adf4 */
extern uint32_t audio_uart_listener_slave3(void *,const void *,uint32_t,uint32_t); /* 0x45b850 */

static const char module[]="sync.module.framework";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char function_name[]="SyncModuleInit";
static const char queue_name[]="sync_data_queue"; /* ROM0x7895a0 */
static const char m_start[]="Sync module start up as Master";
static const char m_start_short[]="[sync.module.framework]Sync module start up as Master";
static const char s_start[]="Sync module start up as Slave";
static const char s_start_short[]="[sync.module.framework]Sync module start up as Slave";
static const char m_fail[]="!!! TF Module(Master Mode) start failure.";
static const char m_fail_short[]="[sync.module.framework]!!! TF Module(Master Mode) start failure.";
static const char s_fail[]="!!! TF Module(Slave Mode) start failure.";
static const char s_fail_short[]="[sync.module.framework]!!! TF Module(Slave Mode) start failure.";
static const char unknown[]="unknown role,init failed...";
static const char unknown_short[]="[sync.module.framework]unknown role,init failed...";
static const char queue_fail[]="create send data msg queue failed.";
static const char queue_fail_short[]="[sync.module.framework]create send data msg queue failed.";
static const char poll_fail[]="create thread poll failed.";
static const char poll_fail_short[]="[sync.module.framework]create thread poll failed.";
static const char timer_fail[]="create sync timeout detection timer failed.";
static const char timer_fail_short[]="[sync.module.framework]create sync timeout detection timer failed.";
typedef struct {const char *name;uint32_t bits;void *control;uint32_t cb_size;
                void *storage;uint32_t storage_size;} queue_attr;
static void log_state(uint8_t level,uint32_t line,const char *message,
                      const char *short_message) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source_file,function_name,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,short_message,
                                    short_message);
}

uint32_t audio_uart_ready(void) {
    uint8_t role=audio_uart_role_get();
    if(role==1u) {
        log_state(3u,0x62cu,m_start,m_start_short);
        g2_uart_tinyframe=audio_uart_module_new(1u);
        if(g2_uart_tinyframe==0) {
            log_state(2u,0x62fu,m_fail,m_fail_short);
            return UINT32_MAX;
        }
        (void)audio_uart_master_prepare();
        audio_uart_module_listener(g2_uart_tinyframe,0u,
                                   audio_uart_listener_master0);
        audio_uart_module_listener(g2_uart_tinyframe,1u,
                                   audio_uart_listener_common1);
        audio_uart_module_listener(g2_uart_tinyframe,4u,
                                   audio_uart_listener_common4);
    } else if(role==2u) {
        log_state(3u,0x638u,s_start,s_start_short);
        g2_uart_tinyframe=audio_uart_module_new(0u);
        if(g2_uart_tinyframe==0) {
            log_state(2u,0x63bu,s_fail,s_fail_short);
            return UINT32_MAX;
        }
        audio_uart_module_listener(g2_uart_tinyframe,2u,
                                   audio_uart_listener_slave2);
        audio_uart_module_listener(g2_uart_tinyframe,3u,
                                   audio_uart_listener_slave3);
        audio_uart_module_listener(g2_uart_tinyframe,1u,
                                   audio_uart_listener_common1);
        audio_uart_module_listener(g2_uart_tinyframe,4u,
                                   audio_uart_listener_common4);
    } else {
        log_state(2u,0x646u,unknown,unknown_short);
        return UINT32_MAX;
    }
    queue_attr qa={queue_name,0u,g2_uart_send_queue_control,0x50u,
                   g2_uart_send_queue_storage,0x258u};
    g2_uart_send_queue=audio_queue_new(0x96u,4u,&qa);
    if(g2_uart_send_queue==0) {
        log_state(1u,0x64eu,queue_fail,queue_fail_short);
        return UINT32_MAX;
    }
    if(audio_uart_poll_thread_start()!=0u) {
        log_state(1u,0x653u,poll_fail,poll_fail_short);
        return UINT32_MAX;
    }
    if(audio_uart_sync_timer_start()!=0u) {
        log_state(1u,0x658u,timer_fail,timer_fail_short);
        return UINT32_MAX;
    }
    return 0u;
}
