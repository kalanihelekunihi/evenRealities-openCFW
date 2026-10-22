/* Apollo display sender wrappers 0x4441ec, 0x4442d0, 0x4443cc, 0x4444b8.
 * The queue, mutex, and ring cells are initialized by service_prepare0.c. */
#include <stdint.h>

extern void *g2_display_queue;
extern void *g2_display_sender_mutex;
extern uint32_t g2_display_ring[5];
extern int32_t audio_file_mutex_acquire(void *,uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern uint32_t audio_uart_input_ring_write(void *,const void *,uint32_t);
extern int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
extern int32_t audio_ble_hci_boot_log_4733ee(const void *,...);
extern void audio_delay_scheduler_assert(void);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="display_thread";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char long_message[]="send data length more than %d Byte,can't load it,exit ...";
static const char compact_message[]="[display_thread]send data length more than %d Byte,can't load it,exit ...";
static const char start_failure[]="message queue send failed";
static const char refresh_failure[]="reflash :message queue send failed";
static const char close_failure[]="close: message queue send failed";

static int32_t send_display(uint8_t kind,uint32_t id,const void *payload,
                            uint32_t bytes,const char *function,
                            uint32_t line,const char *failure)
{
    if(bytes>0x2800u) {
        uint32_t level=audio_log_level();
        if((level&2u)!=0u)
            audio_log_extended(2u,module,source,function,line,long_message,0x2800u);
        level=audio_log_level();
        if((level&1u)!=0u || (audio_log_level()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,compact_message,
                                        compact_message,0x2800u);
        return -1;
    }
    uint32_t notice[3]={kind,id,bytes};
    (void)audio_file_mutex_acquire(g2_display_sender_mutex,UINT32_MAX);
    (void)audio_uart_input_ring_write(g2_display_ring,payload,bytes);
    (void)audio_file_mutex_release(g2_display_sender_mutex);
    if(audio_cmsis_queue_put(g2_display_queue,notice,0u,1000u)!=0) {
        (void)audio_ble_hci_boot_log_4733ee(failure);
        audio_delay_scheduler_assert();
        for(;;) __asm volatile("nop");
    }
    return 0;
}

/* Stock 0x4441EC (display_startup) */
int32_t audio_uart_slave_display_start(uint32_t id,const void *payload,uint32_t bytes)
{
    return send_display(2u,id,payload,bytes,"display_startup",0x36du,start_failure);
}
/* Stock 0x4442D0 (display_refresh) */
int32_t audio_uart_slave_display_refresh(uint32_t id,const void *payload,uint32_t bytes)
{
    return send_display(3u,id,payload,bytes,"display_refresh",0x38bu,refresh_failure);
}
/* Stock 0x4443CC (display_close) */
int32_t audio_uart_slave_display_stop(uint32_t id,const void *payload,uint32_t bytes)
{
    return send_display(5u,id,payload,bytes,"display_close",0x3a9u,close_failure);
}
/* Stock 0x4444B8 (display_close_all) */
int32_t audio_uart_slave_display_control(const void *payload,uint32_t bytes)
{
    return send_display(8u,0u,payload,bytes,"display_close_all",0x3c5u,close_failure);
}
