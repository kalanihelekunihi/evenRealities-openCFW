/* Native DEV_ResourceInit 0x4c632c, the call edge into hand-record init. */
#include <stdint.h>
struct timer_attributes {const char *name;uint32_t flags;void *control_block;uint32_t control_block_size;};
extern uint8_t audio_device_manager_state[]; /* RAM 0x2000060c */
extern void *audio_device_manager_timer; /* RAM 0x200744c0 */
extern uint8_t audio_device_manager_timer_control_block[44]; /* RAM 0x200735a0 */
extern void audio_device_manager_battery_sync_init(void); /* CHG_InitBatterySync */
extern void audio_ring_battery_callback_wrapper_4ff8d4(void);
extern void audio_box_detect_init_4ac02a(void);
extern uint32_t SVC_Settings_Init(void); /* selected 0x46be10 */
extern uint32_t audio_uart_hand_initialize_466660(void);
extern void *audio_queue_new(uint32_t,uint32_t,const void *);
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *);
extern void audio_device_manager_timer_callback_4c661c(void *);
extern int32_t osTimerStart(void *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="device_mgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\device_mgr\\device_mgr.c";
static const char function[]="DEV_ResourceInit";
static const char timer_name[]="device_mgr_timer";
static const struct timer_attributes timer_attrs={timer_name,0u,audio_device_manager_timer_control_block,44u};
#define LOG(level,line,mask,plain,compact,...) do { \
 if(audio_log_level()&2u)audio_log_extended(level,module,path,function,line,plain,##__VA_ARGS__); \
 if((audio_log_level()&1u)||(audio_log_level()&4u)) \
  (void)compressed_log_output(mask,compact,compact,##__VA_ARGS__); \
} while(0)
void audio_device_manager_resource_init_4c632c(void) {
    audio_device_manager_battery_sync_init();
    audio_ring_battery_callback_wrapper_4ff8d4();
    audio_box_detect_init_4ac02a();
    (void)SVC_Settings_Init();
    (void)audio_uart_hand_initialize_466660();
    void **queue=(void **)(void *)(audio_device_manager_state+0x0cu);
    *queue=audio_queue_new(50u,8u,0);
    if(*queue==0) {
        LOG(1u,0xa7u,0x04000000u,
            "[DEV_ResourceInit]osMessageQueueNew fail",
            "[device_mgr][DEV_ResourceInit]osMessageQueueNew fail");
    } else {
        LOG(4u,0xabu,0x10400000u,
            "[DEV_ResourceInit]osMessageQueueNew:0x%x, success",
            "[device_mgr][DEV_ResourceInit]osMessageQueueNew:0x%x, success",*queue);
    }
    if(audio_device_manager_timer==0) {
        audio_device_manager_timer=audio_uart_timer_new(audio_device_manager_timer_callback_4c661c,
                                                         1u,0,&timer_attrs);
        if(audio_device_manager_timer==0) {
            LOG(1u,0xb5u,0x04000000u,
                "[DEV_ResourceInit]osTimerNew failed",
                "[device_mgr][DEV_ResourceInit]osTimerNew failed");
        } else {
            LOG(4u,0xb9u,0x10000000u,
                "[DEV_ResourceInit]osTimerNew success",
                "[device_mgr][DEV_ResourceInit]osTimerNew success");
            (void)osTimerStart(audio_device_manager_timer,1000u);
        }
    }
}
