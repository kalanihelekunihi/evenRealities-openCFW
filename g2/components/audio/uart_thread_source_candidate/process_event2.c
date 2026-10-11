/* SyncModuleSendDataHandler native 0x45e664: drain send queue, construct a
 * TinyFrame multipart frame, dispatch callbacks by message type and free on
 * listener-registration failure. Descendant TinyFrame operations remain
 * explicit code imports. */
#include <stdint.h>
extern void *g2_uart_send_queue; /* RAM0x200749cc */
extern void *g2_uart_tinyframe; /* RAM0x200749c4 */
extern int32_t audio_uart_queue_receive(void *,void *,uint32_t,uint32_t); /* 0x449b3c */
extern uint32_t audio_uart_module_multipart_begin(void *,void *,void *,void *,
                                                 uint32_t); /* 0x492266 -> 0x49224c */
extern void audio_uart_module_multipart_payload(void *,const void *,uint32_t); /* 0x492278 */
extern void audio_uart_module_multipart_close(void *); /* 0x492280 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern uint32_t audio_mask_save(void); /* 0x5fa0a4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_send_begin0(void),audio_uart_send_end0(void); /* 0x45daa0/0x45dc84 */
extern void audio_uart_send_begin_type2(void),audio_uart_send_end_type2(void); /* 0x45e024/0x45e5a4 */
extern void audio_uart_send_begin_type1(void),audio_uart_send_end_type1(void); /* 0x45d7e4/0x45d9cc */
extern void audio_uart_send_begin3(void),audio_uart_send_end3(void); /* 0x45dd68/0x45df24 */
extern void audio_uart_send_begin4(void),audio_uart_send_end4(void); /* 0x45d554/0x45d710 */

static const char module[]="sync.module.framework";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char function_name[]="SyncModuleSendDataHandler";
static const char null_message[]="sync data is null,ignore it...";
static const char null_short[]="[sync.module.framework]sync data is null,ignore it...";
static const char receive_message[]="sync module received data,len = %d";
static const char receive_short[]="[sync.module.framework]sync module received data,len = %d";
static const char listener_message[]="TinyFrame add listener failed!";
static const char listener_short[]="[sync.module.framework]TinyFrame add listener failed!";
static const char payload_message[]="TF_Multipart_Payload send, len = %d";
static const char payload_short[]="[sync.module.framework]TF_Multipart_Payload send, len = %d";
static const char close_message[]="TF_Multipart_Close send";
static const char close_short[]="[sync.module.framework]TF_Multipart_Close send";

typedef struct {uint32_t id;uint16_t type;uint16_t size;void *payload;} send_node;
typedef struct {uint32_t flags;uint16_t type;uint16_t pad;void *payload;
                uint16_t size;uint16_t pad2;send_node *node;uint32_t id;} frame;
_Static_assert(sizeof(frame)==24,"native TinyFrame send frame size");
static void log_send(uint8_t level,uint32_t line,const char *long_message,
                     const char *short_message,uint32_t arg,uint8_t has_arg) {
    if(audio_log_flags()&2u) {
        if(has_arg) audio_log_extended(level,module,source_file,function_name,
                                       line,long_message,arg);
        else audio_log_extended(level,module,source_file,function_name,
                                line,long_message);
    }
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) {
        uint32_t category=(uint32_t)level<<26;
        if(has_arg) category|=0x400000u;
        if(has_arg)(void)compressed_log_output(category,short_message,
                                                short_message,arg);
        else (void)compressed_log_output(category,short_message,short_message);
    }
}
void audio_uart_process_event2(void) {
    send_node *node=0;
    for(;;) {
        if(audio_uart_queue_receive(g2_uart_send_queue,&node,0u,0u)!=0) return;
        if(node==0) {
            log_send(2u,0x5e2u,null_message,null_short,0u,0u);
            continue;
        }
        log_send(4u,0x5e5u,receive_message,receive_short,node->size,1u);
        frame f={0};
        f.node=node;
        f.id=node->id;
        f.type=node->type;
        f.size=node->size;
        void (*begin)(void)=0;
        void (*end)(void)=0;
        switch(node->type) {
        case 0: begin=audio_uart_send_begin0;end=audio_uart_send_end0;break;
        case 1: begin=audio_uart_send_begin_type1;end=audio_uart_send_end_type1;break;
        case 2: begin=audio_uart_send_begin_type2;end=audio_uart_send_end_type2;break;
        case 3: begin=audio_uart_send_begin3;end=audio_uart_send_end3;break;
        case 4: begin=audio_uart_send_begin4;end=audio_uart_send_end4;break;
        default:
            (void)audio_mask_save();
            for(;;) __asm__ volatile("nop");
        }
        uint32_t added=audio_uart_module_multipart_begin(g2_uart_tinyframe,
                              &f,(void *)begin,(void *)end,0x32u);
        if((uint8_t)added==0u) {
            log_send(2u,0x613u,listener_message,listener_short,0u,0u);
            audio_file_heap_free(node->payload);
            audio_file_heap_free(node);
        } else {
            audio_uart_module_multipart_payload(g2_uart_tinyframe,
                                                 node->payload,node->size);
            log_send(4u,0x61cu,payload_message,payload_short,node->size,1u);
            audio_uart_module_multipart_close(g2_uart_tinyframe);
            log_send(4u,0x61fu,close_message,close_short,0u,0u);
        }
    }
}
