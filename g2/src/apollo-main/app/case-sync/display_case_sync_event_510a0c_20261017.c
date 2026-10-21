/* Stock Main APP_PbRxGlassesCaseFrameDataProcess, 0x510a0c. */
#include <stdint.h>
struct case_istream {void *callback;void *state;uint32_t bytes_left;const char *errmsg;};
_Static_assert(sizeof(struct case_istream)==16u,"nanopb input stream ABI");
extern uint8_t audio_uart_case_rx_frame_200f5a90[10];
extern const uint8_t audio_uart_case_descriptor_77793c[];
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_uart_pb_stream_init(struct case_istream *,const void *,uint32_t);
extern void *audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_pb_decode(void *,const void *,void *);
extern uint32_t audio_uart_case_rx_info_510bfe(uint32_t,const uint8_t *);
extern uint32_t audio_uart_case_send_response_510c70(uint32_t,const uint8_t *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.glasses_case";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_glasses_case\\pb_service_glasses_case.c";
static const char function_name[]="APP_PbRxGlassesCaseFrameDataProcess";
static const char none[]="(none)";
static void log_plain(uint8_t level,uint32_t line,const char *message,const char *compact)
{
    if (audio_log_level()&2u) audio_log_extended(level,module,path,function_name,line,message);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output((uint32_t)level<<26u,compact,compact);
}
static void log_number(uint8_t level,uint32_t line,const char *message,const char *compact,uint32_t value)
{
    if (audio_log_level()&2u) audio_log_extended(level,module,path,function_name,line,message,value);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(((uint32_t)level<<26u)|0x00400000u,compact,compact,value);
}

uint32_t audio_uart_case_sync_event_510a0c(const uint8_t *data,uint32_t length_arg)
{
    uint16_t length=(uint16_t)length_arg;
    log_number(4u,0x2fu,"len=%d","[pb.glasses_case]len=%d",length);
    if (data==0) {
        log_plain(1u,0x31u,"pData is NULL","[pb.glasses_case]pData is NULL");
        return 2u;
    }
    uint8_t *const frame=audio_uart_case_rx_frame_200f5a90;
    audio_uart_buffer_zero(frame,10u,0u);
    struct case_istream initial,stream;
    audio_uart_pb_stream_init(&initial,data,length);
    (void)audio_uart_checksum_copy(&stream,&initial,16u);
    if ((uint8_t)audio_uart_pb_decode(&stream,audio_uart_case_descriptor_77793c,frame)==0u) {
        const char *why=stream.errmsg!=0?stream.errmsg:none;
        if (audio_log_level()&2u)
            audio_log_extended(1u,module,path,function_name,0x3bu,"Decoding failed: %s",why);
        if ((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04400000u,
                "[pb.glasses_case]Decoding failed: %s",
                "[pb.glasses_case]Decoding failed: %s",why);
        return 43u;
    }
    log_number(4u,0x3fu,"glasses_case command_id: %d",
               "[pb.glasses_case]glasses_case command_id: %d",frame[0]);
    if (frame[0]==1u) {
        if (audio_uart_case_rx_info_510bfe(frame[1],frame+4u)==0u)
            return audio_uart_case_send_response_510c70(frame[1],frame+4u);
        return 1u;
    }
    log_number(2u,0x4cu,"Unknown command_id: %d",
               "[pb.glasses_case]Unknown command_id: %d",frame[0]);
    return 1u;
}
