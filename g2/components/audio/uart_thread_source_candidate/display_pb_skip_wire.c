/* Native nanopb unknown-wire dispatcher 0x48f6a0 and varint skip 0x48f628.
 * The stream and length-delimited lower routines are authentic typed imports.
 */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state; uint32_t bytes_left; const char *errmsg;
};
_Static_assert(sizeof(struct pb_istream_candidate)==16u,"native input stream size");
extern uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *,void *,uint32_t);
extern uint32_t audio_pb_skip_length_48f64c(struct pb_istream_candidate *);
static const char pb_invalid_wire_type[]="invalid wire_type"; /* ROM 0x7817dc */

uint32_t audio_pb_skip_varint_48f628(struct pb_istream_candidate *s)
{
    uint8_t byte;
    do {
        if (!audio_pb_read_stream_48f3be(s,&byte,1u)) return 0u;
    } while ((byte&128u)!=0u);
    return 1u;
}

uint32_t audio_pb_skip_wire_48f6a0(struct pb_istream_candidate *s,uint32_t wire_type)
{
    switch (wire_type&255u) {
    case 0u: return audio_pb_skip_varint_48f628(s);
    case 1u: return audio_pb_read_stream_48f3be(s,0,8u);
    case 2u: return audio_pb_skip_length_48f64c(s);
    case 5u: return audio_pb_read_stream_48f3be(s,0,4u);
    default:
        if (s->errmsg==0) s->errmsg=pb_invalid_wire_type;
        return 0u;
    }
}
