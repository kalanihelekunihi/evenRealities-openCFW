/* Native Main _thread_msg_handler 0x4c4de8, draining the queue and
 * dispatching all four authenticated message IDs. */
#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
extern struct ring_thread_manager audio_uart_ring_thread_manager; /* RAM 0x20004120 */
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* selected 0x449b3c */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void audio_uart_ring_send_packet_472988(const void *,uint32_t);
extern void audio_uart_ring_message_80_472378(uint8_t);
extern void audio_uart_ring_message_400_4723d6(uint8_t,uint8_t);
extern void audio_uart_ring_message_1000_4722d8(uint16_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char fn[]="_thread_msg_handler";
static const char receive[]="ring task RX: msg_id = %d, msg_len = %d";
static const char receive_short[]="[task.ring]ring task RX: msg_id = %d, msg_len = %d";
void audio_uart_ring_msg_handler_4c4de8(void) {
    for(;;) {
        uint8_t *msg=0;
        int32_t status=audio_uart_queue_receive(audio_uart_ring_thread_manager.queue,&msg,0u,0u);
        if(status!=0 || msg==0)break;
        uint32_t id=*(uint32_t *)(void *)msg;
        uint32_t length=*(uint32_t *)(void *)(msg+4u);
        if(id==2u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(4u,module,path,fn,192u,receive,id,length);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x10800000u,receive_short,receive_short,id,length);
            audio_uart_ring_send_packet_472988(msg+8u,(uint16_t)length);
        } else if(id==0x80u) {
            if(length!=0u)audio_uart_ring_message_80_472378(msg[8]);
        } else if(id==0x400u) {
            if(length!=0u)audio_uart_ring_message_400_4723d6(msg[8],msg[9]);
        } else if(id==0x1000u && length>1u) {
            audio_uart_ring_message_1000_4722d8((uint16_t)(((uint16_t)msg[8]<<8)|msg[9]));
        }
        audio_file_heap_free(msg);
    }
}
