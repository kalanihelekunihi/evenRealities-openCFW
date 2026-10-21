/* Native nanopb wire-key constructors 0x490d66 and 0x490d4a. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
struct pb_field_iter_candidate {
    const void *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size; const void *submessage_descriptor;
};
extern uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *,uint32_t,uint32_t,uint32_t);
static const char pb_invalid_field_type[]="invalid field type"; /* ROM 0x781854 via 0x4910c0 */
uint32_t audio_pb_encode_key_490d4a(struct pb_ostream_candidate *stream,uint32_t wire_type,uint32_t tag)
{
    uint32_t low=(tag<<3)|(wire_type&255u);
    uint32_t high=tag>>29;
    return audio_pb_write_varint_490ce0(stream,wire_type&255u,low,high);
}
uint32_t audio_pb_encode_tag_490d66(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    uint32_t type=iter->type&15u;
    uint32_t wire_type;
    if (type<=3u) wire_type=0u;
    else if (type==4u) wire_type=5u;
    else if (type==5u) wire_type=1u;
    else if ((type>=6u && type<=9u) || type==11u) wire_type=2u;
    else {
        if (stream->errmsg==0) stream->errmsg=pb_invalid_field_type;
        return 0u;
    }
    return audio_pb_encode_key_490d4a(stream,wire_type,iter->tag);
}
