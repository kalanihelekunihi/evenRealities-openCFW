/* Stock Main APP_PbTxEncodeGlassesCaseInfo, 0x510c70, with local status getters. */
#include <stdint.h>
struct case_ostream {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct case_ostream)==20u,"nanopb output stream ABI");
struct case_fault {uint32_t code;uint16_t kind;uint16_t reserved;const char *path;const char *function;uint32_t line;};
_Static_assert(sizeof(struct case_fault)==20u,"fault record ABI");
extern volatile uint8_t g2_uart_service_nonce[4]; /* stock RAM 0x20074928 */
extern uint8_t audio_uart_case_tx_frame_200f5a9c[10];
extern uint8_t audio_uart_case_tx_encoded_2037c5a0[256];
extern const uint8_t audio_uart_case_descriptor_77793c[];
extern void *audio_uart_checksum_copy(void *,const void *,uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern void audio_pb_ostream_from_buffer(struct case_ostream *,void *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_pb_encode(struct case_ostream *,const void *,const void *);
extern uint32_t audio_uart_case_status(void);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
static const char module[]="pb.glasses_case";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_glasses_case\\pb_service_glasses_case.c";
static const char function_name[]="APP_PbTxEncodeGlassesCaseInfo";
static const char none[]="(none)";

__attribute__((noinline)) uint8_t audio_uart_case_local_soc_4ac726(void) {return g2_uart_service_nonce[0];}
__attribute__((noinline)) uint8_t audio_uart_case_local_charge_4ac73c(void) {return g2_uart_service_nonce[1];}
__attribute__((noinline)) uint8_t audio_uart_case_local_lid_4ac752(void) {return g2_uart_service_nonce[2];}

uint32_t audio_uart_case_send_response_510c70(uint32_t sequence,const uint8_t *unused)
{
    (void)unused;
    if (unused==0) {
        static const struct case_fault template={0u,0u,0u,path,function_name,0x64u};
        struct case_fault fault;
        (void)audio_uart_checksum_copy(&fault,&template,20u);
        fault.kind=1u;
        audio_ring_pb_assert_509b48(&fault);
        if (audio_log_level()&2u)
            audio_log_extended(1u,module,path,function_name,0x66u,"POINTER NULL");
        if ((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04000000u,
                "[pb.glasses_case]POINTER NULL","[pb.glasses_case]POINTER NULL");
        return 2u;
    }
    struct case_ostream initial,stream;
    uint8_t *const encoded=audio_uart_case_tx_encoded_2037c5a0;
    uint8_t *const frame=audio_uart_case_tx_frame_200f5a9c;
    audio_pb_ostream_from_buffer(&initial,encoded,256u);
    (void)audio_uart_checksum_copy(&stream,&initial,20u);
    audio_uart_buffer_zero(frame,10u,0u);
    frame[0]=1u;
    frame[1]=(uint8_t)sequence;
    frame[2]=3u;frame[3]=0u;
    frame[4]=audio_uart_case_local_soc_4ac726();
    frame[5]=audio_uart_case_local_charge_4ac73c();
    frame[6]=audio_uart_case_local_lid_4ac752();
    frame[7]=audio_uart_case_status()==1u?1u:0u;
    frame[8]=0u;
    uint32_t encoded_ok=audio_pb_encode(&stream,audio_uart_case_descriptor_77793c,frame);
    if (audio_log_level()&2u)
        audio_log_extended(4u,module,path,function_name,0x7du,"txLen = %d",
                           (uint16_t)stream.bytes_written);
    if ((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10400000u,
            "[pb.glasses_case]txLen = %d","[pb.glasses_case]txLen = %d",
            (uint16_t)stream.bytes_written);
    if ((uint8_t)encoded_ok==0u) {
        const char *why=stream.errmsg!=0?stream.errmsg:none;
        if (audio_log_level()&2u)
            audio_log_extended(1u,module,path,function_name,0x80u,"Encoding failed: %s\n",why);
        if ((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x04400000u,
                "[pb.glasses_case]Encoding failed: %s\n",
                "[pb.glasses_case]Encoding failed: %s\n",why);
        return 43u;
    }
    (void)audio_ring_pb_tx_ble_475b14(1u,0x81u,encoded,(uint16_t)stream.bytes_written);
    return 0u;
}
