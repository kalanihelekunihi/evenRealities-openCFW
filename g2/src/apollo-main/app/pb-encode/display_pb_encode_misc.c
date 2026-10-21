/* Native nanopb bool, fixed-length bytes, and submessage dispatch. */
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
extern uint32_t audio_pb_first_char_nonzero_490678(const void *);
extern uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_pb_write_length_delimited_490db6(struct pb_ostream_candidate *,const void *,uint32_t);
extern uint32_t audio_pb_write_submessage_490ddc(struct pb_ostream_candidate *,const void *,const void *);
static const char pb_invalid_field_descriptor[]="invalid field descriptor"; /* 0x76f470 */
uint32_t audio_pb_encode_bool_490e90(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    uint32_t value=audio_pb_first_char_nonzero_490678(iter->data)!=0u;
    return audio_pb_write_varint_490ce0(stream,0u,value,0u);
}
uint32_t audio_pb_encode_fixed_length_bytes_4910e8(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    return audio_pb_write_length_delimited_490db6(stream,iter->data,iter->data_size);
}
uint32_t audio_pb_encode_submessage_49104c(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    if (iter->submessage_descriptor==0) {
        if (stream->errmsg==0) stream->errmsg=pb_invalid_field_descriptor;
        return 0u;
    }
    if ((iter->type&15u)==9u && iter->size!=0) {
        uint8_t *ptr=(uint8_t *)iter->size-8u;
        uint32_t (*callback)(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *,void *)=
            *(uint32_t (**)(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *,void *))ptr;
        if (callback!=0 && !callback(stream,iter,ptr+4u)) return 0u;
    }
    return audio_pb_write_submessage_490ddc(stream,iter->submessage_descriptor,iter->data);
}
