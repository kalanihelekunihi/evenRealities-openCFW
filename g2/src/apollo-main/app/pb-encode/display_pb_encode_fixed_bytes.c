/* Native nanopb fixed, bytes, and length-delimited providers. */
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
extern uint32_t audio_pb_stream_write_490616(struct pb_ostream_candidate *,const void *,uint32_t);
extern uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *,uint32_t,uint32_t,uint32_t);
static const char pb_invalid_data_size[]="invalid data_size"; /* 0x781890 */
static const char pb_bytes_size_exceeded[]="bytes size exceeded"; /* 0x7818a4 */
uint32_t audio_pb_write_fixed32_490d36(struct pb_ostream_candidate *stream,const void *data)
{ return audio_pb_stream_write_490616(stream,data,4u); }
uint32_t audio_pb_write_fixed64_490d40(struct pb_ostream_candidate *stream,const void *data)
{ return audio_pb_stream_write_490616(stream,data,8u); }
uint32_t audio_pb_encode_fixed_490f72(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    if (iter->data_size==4u) return audio_pb_write_fixed32_490d36(stream,iter->data);
    if (iter->data_size==8u) return audio_pb_write_fixed64_490d40(stream,iter->data);
    if (stream->errmsg==0) stream->errmsg=pb_invalid_data_size;
    return 0u;
}
uint32_t audio_pb_write_length_delimited_490db6(struct pb_ostream_candidate *stream,const void *data,uint32_t size)
{
    if (!audio_pb_write_varint_490ce0(stream,(uint32_t)(uintptr_t)data,size,0u)) return 0u;
    return audio_pb_stream_write_490616(stream,data,size);
}
uint32_t audio_pb_encode_bytes_490fa2(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    const uint16_t *bytes=(const uint16_t *)iter->data;
    if (bytes==0) return audio_pb_write_length_delimited_490db6(stream,0,0u);
    if ((iter->type&0xc0u)==0u && ((uint32_t)iter->data_size-2u)<(uint32_t)*bytes) {
        if (stream->errmsg==0) stream->errmsg=pb_bytes_size_exceeded;
        return 0u;
    }
    return audio_pb_write_length_delimited_490db6(stream,bytes+1,*bytes);
}
