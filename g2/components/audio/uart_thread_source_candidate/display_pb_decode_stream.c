/* Native nanopb buffer reader, stream read, and length skip:
 * 0x48f3a4, 0x48f3be, 0x48f64c. These are real stream effects.
 */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state;uint32_t bytes_left;const char *errmsg;
};
_Static_assert(sizeof(struct pb_istream_candidate)==16u,"native input stream size");
static const char pb_end_of_stream[]="end-of-stream"; /* ROM 0x787c70 */
static const char pb_io_error[]="io error"; /* ROM 0x78b690 */
extern uint32_t audio_pb_read_varint_48f4b8(struct pb_istream_candidate *,uint32_t *,uint8_t *);

uint32_t audio_pb_buffer_read_48f3a4(void *stream,void *out,uint32_t n)
{
    struct pb_istream_candidate *s=(struct pb_istream_candidate *)stream;
    const uint8_t *source=(const uint8_t *)s->state;
    s->state=(void *)(source+n);
    if (out!=0) {
        uint8_t *dest=(uint8_t *)out;
        for (uint32_t i=0;i<n;++i) dest[i]=source[i];
    }
    return 1u;
}

uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *s,void *out,uint32_t n)
{
    if (n==0u) return 1u;
    if (out==0 && s->callback!=audio_pb_buffer_read_48f3a4) {
        uint8_t scratch[16];
        while (n>16u) {
            if (!audio_pb_read_stream_48f3be(s,scratch,16u)) return 0u;
            n-=16u;
        }
        return audio_pb_read_stream_48f3be(s,scratch,n);
    }
    if (s->bytes_left<n) {
        if (s->errmsg==0) s->errmsg=pb_end_of_stream;
        return 0u;
    }
    if (!s->callback(s,out,n)) {
        if (s->errmsg==0) s->errmsg=pb_io_error;
        return 0u;
    }
    if (s->bytes_left<n) s->bytes_left=0u;
    else s->bytes_left-=n;
    return 1u;
}

uint32_t audio_pb_skip_length_48f64c(struct pb_istream_candidate *s)
{
    uint32_t n;
    if (!audio_pb_read_varint_48f4b8(s,&n,0)) return 0u;
    return audio_pb_read_stream_48f3be(s,0,n);
}
