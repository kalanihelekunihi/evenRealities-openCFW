/* Stock Main APP_PbNotifyEncodeGlassesCaseInfo 0x510dec. */
#include <stdint.h>

struct case_ostream {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct case_ostream)==20u,"nanopb ostream ABI");
struct case_fault {uint32_t code;uint16_t kind;uint16_t reserved;const char *path;const char *function;uint32_t line;};
_Static_assert(sizeof(struct case_fault)==20u,"fault record ABI");
extern uint8_t audio_uart_case_tx_frame_200f5a9c[10];
extern uint8_t audio_uart_case_tx_encoded_2037c5a0[256];
extern uint8_t audio_uart_case_tx_magic_20074ffa;
extern const uint8_t audio_uart_case_descriptor_77793c[];
extern void *audio_uart_display_area_copy_439c04(void *,const void *,uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern void audio_pb_ostream_from_buffer(struct case_ostream *,void *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_pb_encode(struct case_ostream *,const void *,const void *);
extern uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.glasses_case";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_glasses_case\\pb_service_glasses_case.c";
static const char function_name[]="APP_PbNotifyEncodeGlassesCaseInfo";
static const char none[]="(none)";
static void log0(uint8_t level,uint32_t line,const char *message,uint32_t code,const char *compact)
{
    if (audio_log_level()&2u) audio_log_extended(level,module,path,function_name,line,message);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact);
}
static void log1(uint8_t level,uint32_t line,const char *message,uint32_t code,
                 const char *compact,uint32_t value)
{
    if (audio_log_level()&2u) audio_log_extended(level,module,path,function_name,line,message,value);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(code,compact,compact,value);
}
static void log_error(const char *why)
{
    static const char message[]="Encoding failed: %s\n";
    static const char compact[]="[pb.glasses_case]Encoding failed: %s\n";
    if (audio_log_level()&2u) audio_log_extended(1u,module,path,function_name,0xa7u,message,why);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04400000u,compact,compact,why);
}

uint32_t audio_uart_case_send_status_510dec(uint32_t unused,const uint8_t *packet)
{
    (void)unused;
    if (packet==0) {
        static const struct case_fault fault_template={0u,0u,0u,path,function_name,0x8au};
        struct case_fault fault;
        (void)audio_uart_display_area_copy_439c04(&fault,&fault_template,20u);
        fault.kind=1u;
        audio_ring_pb_assert_509b48(&fault);
        log0(1u,0x8cu,"POINTER NULL",0x04000000u,"[pb.glasses_case]POINTER NULL");
        return 2u;
    }
    struct case_ostream initial,stream;
    uint8_t *const encoded=audio_uart_case_tx_encoded_2037c5a0;
    uint8_t *const frame=audio_uart_case_tx_frame_200f5a9c;
    audio_pb_ostream_from_buffer(&initial,encoded,256u);
    (void)audio_uart_display_area_copy_439c04(&stream,&initial,20u);
    audio_uart_buffer_zero(frame,10u,0u);
    frame[0]=1u;
    frame[1]=audio_uart_case_tx_magic_20074ffa;
    audio_uart_case_tx_magic_20074ffa=(uint8_t)(audio_uart_case_tx_magic_20074ffa+1u);
    frame[2]=3u;frame[3]=0u;
    frame[4]=packet[0];frame[5]=packet[1];frame[6]=packet[2];frame[7]=packet[3];
    frame[8]=0u;
    uint32_t encoded_ok=audio_pb_encode(&stream,audio_uart_case_descriptor_77793c,frame);
    log1(4u,0xa3u,"txLen = %d",0x10400000u,"[pb.glasses_case]txLen = %d",
         (uint16_t)stream.bytes_written);
    if ((uint8_t)encoded_ok!=0u) {
        (void)audio_ring_pb_tx_ble_475c1a(1u,0x81u,encoded,(uint16_t)stream.bytes_written);
        return 0u;
    }
    log_error(stream.errmsg!=0?stream.errmsg:none);
    return 43u;
}
