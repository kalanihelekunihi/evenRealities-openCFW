/* Stock Apollo APP_PbTxEncodeRingEvent 0x5ce4e6. */
#include <stdint.h>
#include "ring_buffers.h"

struct ring_pb_ostream {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
struct ring_fault_record {
    uint32_t code, detail;
    const char *path, *function;
    uint32_t line;
};
_Static_assert(sizeof(struct ring_pb_ostream)==20u,"nanopb ostream ABI");
_Static_assert(sizeof(struct ring_fault_record)==20u,"fault record ABI");

struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate audio_ring_pb_descriptor; /* native 0x77b104 */
extern void audio_ring_pb_assert_509b48(void *); /* 0x509b48 */
extern void audio_pb_ostream_from_buffer(struct ring_pb_ostream *,void *,uint32_t); /* 0x4905f4 */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern uint32_t audio_pb_encode(void *,const void *,const void *); /* 0x490c32 */
extern void audio_ring_pb_tx_ble_475b14(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* 0x43ce9e */

static const char module[]="pb.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_ring\\pb_service_ring.c";
static const char function[]="APP_PbTxEncodeRingEvent";
static const char null_message[]="POINTER NULL";
static const char null_short[]="[pb.ring]POINTER NULL";
static const char length_message[]="txLen = %d";
static const char length_short[]="[pb.ring]txLen = %d";
static const char encode_error[]="Encoding failed: %s\n";
static const char encode_error_short[]="[pb.ring]Encoding failed: %s\n";
static const char none[]="(none)";

uint32_t audio_ring_command_dispatch_5ce4e6(uint32_t command_id,const void *event) {
    if(event==0) {
        static const struct ring_fault_record template={0u,0u,path,function,0x82u};
        struct ring_fault_record fault;
        audio_uart_checksum_copy(&fault,&template,20u);
        fault.detail=1u;
        audio_ring_pb_assert_509b48(&fault);
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x84u,null_message);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 2u;
    }
    struct ring_pb_ostream initial,stream;
    audio_pb_ostream_from_buffer(&initial,audio_ring_tx_buffer,0x100u);
    audio_uart_checksum_copy(&stream,&initial,20u);
    audio_uart_buffer_zero(audio_ring_buffers.encode,64u,0u);
    const uint8_t *input=event;
    uint8_t *output=audio_ring_buffers.encode;
    output[0]=1u;
    output[1]=(uint8_t)command_id;
    output[2]=3u;output[3]=0u;
    output[12]=input[8];
    for(uint32_t i=0;i<4u;i++) output[16u+i]=input[12u+i];
    uint16_t size=(uint16_t)((uint16_t)input[0]|((uint16_t)input[1]<<8u));
    output[4]=(uint8_t)size;output[5]=(uint8_t)(size>>8u);
    if(size!=0u && size<7u)
        (void)audio_queue_copy_bytes(output+6u,input+2u,size);
    output[20]=0u;
    uint32_t encoded=audio_pb_encode(&stream,&audio_ring_pb_descriptor,output)&255u;
    uint16_t written=(uint16_t)stream.bytes_written;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x9du,length_message,written);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,length_short,length_short,written);
    if(encoded==0u) {
        const char *error=stream.errmsg?stream.errmsg:none;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0xa0u,encode_error,error);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,encode_error_short,
                                        encode_error_short,error);
        return 0x2bu;
    }
    audio_ring_pb_tx_ble_475b14(1u,0x91u,audio_ring_tx_buffer,written);
    return 0u;
}
