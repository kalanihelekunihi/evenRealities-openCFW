/* Apollo display-driver timer callback 0x473b54..0x473bc3. Candidate. */
#include <stdint.h>
struct display_driver_manager {
    void (*thread_init)(void);
    void (*queue_init)(void);
    void *thread;
    void *queue;
};
_Static_assert(sizeof(struct display_driver_manager)==16u,"display driver manager ABI");
extern struct display_driver_manager audio_display_driver_manager; /* SRAM 0x20000658 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* 0x449abe */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.displaydrvmgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char function[]="display_device_timer_callback";
static const char text[]="async_reflash_xQueue1 send failed..\r\n";
static const char compact[]="[task.displaydrvmgr]async_reflash_xQueue1 send failed..\r\n";
void display_driver_timer_callback_473b54(void *argument) {
    (void)argument;
    uint32_t message[9];
    audio_uart_buffer_zero(message,36u,0u);
    message[0]=6u;
    if(audio_cmsis_queue_put(audio_display_driver_manager.queue,message,0u,1000u)==0)
        return;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,0xb5u,text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08000000u,compact,compact);
}
