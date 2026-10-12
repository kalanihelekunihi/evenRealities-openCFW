/* Native nanopb bool/fixed-width scalar readers 0x4901cc, 0x490190,
 * 0x4901ac. The native bool lower is 0x49012c.
 */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_field_iter_candidate { const void *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const void *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_read_varint_48f4b8(struct pb_istream_candidate *,uint32_t *,uint8_t *);
extern uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *,void *,uint32_t);

uint32_t audio_pb_decode_bool_4901cc(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    uint32_t value;
    if (!audio_pb_read_varint_48f4b8(s,&value,0)) return 0u;
    *(uint8_t *)it->data=(uint8_t)(value!=0u);
    return 1u;
}
uint32_t audio_pb_decode_fixed32_490190(struct pb_istream_candidate *s,void *out)
{
    uint32_t value;
    if (!audio_pb_read_stream_48f3be(s,&value,4u)) return 0u;
    *(uint32_t *)out=value;
    return 1u;
}
uint32_t audio_pb_decode_fixed64_4901ac(struct pb_istream_candidate *s,void *out)
{
    uint32_t value[2];
    if (!audio_pb_read_stream_48f3be(s,value,8u)) return 0u;
    ((uint32_t *)out)[0]=value[0];
    ((uint32_t *)out)[1]=value[1];
    return 1u;
}
