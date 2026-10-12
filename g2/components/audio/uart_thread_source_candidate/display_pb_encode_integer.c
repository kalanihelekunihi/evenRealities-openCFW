/* Native nanopb integer scalar 0x490eae and zigzag 0x490d08. */
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
static const char pb_invalid_data_size[]="invalid data_size"; /* native 0x781890 via 0x4910d4 */
uint32_t audio_pb_write_zigzag_490d08(struct pb_ostream_candidate *stream,uint32_t type,uint32_t low,int32_t high)
{
    uint64_t value=((uint64_t)(uint32_t)high<<32)|low;
    uint64_t encoded=(value<<1)^(uint64_t)-(int64_t)(value>>63);
    return audio_pb_write_varint_490ce0(stream,type,(uint32_t)encoded,(uint32_t)(encoded>>32));
}
uint32_t audio_pb_encode_int_490eae(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    uint32_t low,high;
    uint32_t type=iter->type&15u;
    if (type==2u) {
        switch (iter->data_size) {
        case 1u: low=*(const uint8_t *)iter->data; high=0u; break;
        case 2u: low=*(const uint16_t *)iter->data; high=0u; break;
        case 4u: low=*(const uint32_t *)iter->data; high=0u; break;
        case 8u: low=((const uint32_t *)iter->data)[0]; high=((const uint32_t *)iter->data)[1]; break;
        default: goto invalid_size;
        }
        return audio_pb_write_varint_490ce0(stream,(uint32_t)(uintptr_t)iter->data,low,high);
    }
    switch (iter->data_size) {
    case 1u: { int32_t v=*(const int8_t *)iter->data; low=(uint32_t)v; high=(uint32_t)(v>>31); break; }
    case 2u: { int32_t v=*(const int16_t *)iter->data; low=(uint32_t)v; high=(uint32_t)(v>>31); break; }
    case 4u: { int32_t v=*(const int32_t *)iter->data; low=(uint32_t)v; high=(uint32_t)(v>>31); break; }
    case 8u: low=((const uint32_t *)iter->data)[0]; high=((const uint32_t *)iter->data)[1]; break;
    default: goto invalid_size;
    }
    if (type==3u) return audio_pb_write_zigzag_490d08(stream,type,low,(int32_t)high);
    return audio_pb_write_varint_490ce0(stream,type,low,high);
invalid_size:
    if (stream->errmsg==0) stream->errmsg=pb_invalid_data_size;
    return 0u;
}
