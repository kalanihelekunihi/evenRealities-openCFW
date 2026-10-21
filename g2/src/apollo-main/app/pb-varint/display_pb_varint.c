/* Native nanopb varint dispatch 0x490ce0 and 64-bit emission 0x490c84. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
extern uint32_t audio_pb_stream_write_490616(struct pb_ostream_candidate *,const void *,uint32_t);
uint32_t audio_pb_write_varint_long_490c84(struct pb_ostream_candidate *stream,uint32_t low,uint32_t high)
{
    uint64_t value=((uint64_t)high<<32)|low;
    uint8_t bytes[10]; uint32_t count=0;
    do {
        uint8_t part=(uint8_t)(value&0x7fu);
        value>>=7;
        bytes[count++]=(uint8_t)(part|(value?0x80u:0u));
    } while (value);
    return audio_pb_stream_write_490616(stream,bytes,count);
}
uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *stream,uint32_t unused_wire_type,uint32_t low,uint32_t high)
{
    (void)unused_wire_type;
    if (high==0u && low<128u) {
        uint8_t byte=(uint8_t)low;
        return audio_pb_stream_write_490616(stream,&byte,1u);
    }
    return audio_pb_write_varint_long_490c84(stream,low,high);
}
