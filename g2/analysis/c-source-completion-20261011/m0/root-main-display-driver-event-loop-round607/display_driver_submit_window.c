/* Apollo display command packaging 0x474066..0x4740ff. Candidate. */
#include <stdint.h>
typedef struct { uint32_t id,arg[8]; } display_driver_window_message;
_Static_assert(sizeof(display_driver_window_message)==0x24u,"native queue message");
typedef struct { void (*thread_init)(void);void (*queue_init)(void);void *thread;void *queue; } display_driver_manager_prefix;
extern display_driver_manager_prefix audio_display_driver_manager; /* selected 0x20000658 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t); /* selected 0x449abe */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.displaydrvmgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char function[]="send_async_reflash_msg";
static const char failure[]="Error - Failed to send ASYNC_REFLASH_COMMAND\r\n";
static const char compact[]="[task.displaydrvmgr]Error - Failed to send ASYNC_REFLASH_COMMAND\r\n";
uint32_t display_driver_submit_window_474066(uint32_t a,uint32_t b,uint32_t c,
                                             uint32_t d,uint32_t e,uint32_t f) {
    display_driver_window_message message;
    audio_uart_buffer_zero(&message,0x24u,0u);
    message.id=3u;
    message.arg[0]=a;message.arg[1]=b;message.arg[2]=c;
    message.arg[3]=d;message.arg[4]=e;message.arg[5]=f;
    if(audio_cmsis_queue_put(audio_display_driver_manager.queue,&message,0u,1000u)!=0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x161u,failure);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,compact,compact);
        return UINT32_MAX;
    }
    return 0u;
}
