/* Native nanopb two-pass submessage writer 0x490ddc. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
extern uint32_t audio_pb_encode(void *,const void *,const void *);
extern uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_pb_stream_write_490616(struct pb_ostream_candidate *,const void *,uint32_t);
static const char pb_stream_full[]="stream full"; /* 0x78b6a8 */
static const char pb_submsg_size_changed[]="submsg size changed"; /* 0x78187c */
uint32_t audio_pb_write_submessage_490ddc(struct pb_ostream_candidate *stream,const void *descriptor,const void *message)
{
    struct pb_ostream_candidate child={0};
    uint32_t expected;
    if (!audio_pb_encode(&child,descriptor,message)) {
        stream->errmsg=child.errmsg;
        return 0u;
    }
    expected=child.bytes_written;
    if (!audio_pb_write_varint_490ce0(stream,0u,expected,0u)) return 0u;
    if (stream->callback==0) return audio_pb_stream_write_490616(stream,0,expected);
    if (stream->max_size<expected+stream->bytes_written) {
        if (stream->errmsg==0) stream->errmsg=pb_stream_full;
        return 0u;
    }
    child.callback=stream->callback;
    child.state=stream->state;
    child.max_size=expected;
    child.bytes_written=0u;
    child.errmsg=0;
    uint32_t ok=audio_pb_encode(&child,descriptor,message);
    stream->bytes_written+=child.bytes_written;
    stream->state=child.state;
    stream->errmsg=child.errmsg;
    if (child.bytes_written!=expected) {
        if (stream->errmsg==0) stream->errmsg=pb_submsg_size_changed;
        return 0u;
    }
    return ok;
}
