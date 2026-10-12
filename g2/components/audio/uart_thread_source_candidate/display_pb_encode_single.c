/* Native nanopb single-field dispatch 0x490a46. */
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
extern uint32_t audio_pb_encode_tag_490d66(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_bool_490e90(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_int_490eae(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_fixed_490f72(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_bytes_490fa2(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_string_490fe4(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_submessage_49104c(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_fixed_length_bytes_4910e8(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
static const char pb_invalid_field_type[]="invalid field type"; /* native 0x781854 via 0x4910c0 */
uint32_t audio_pb_encode_single_490a46(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    uint32_t type=iter->type&15u;
    if (iter->data==0) return 1u;
    if (!audio_pb_encode_tag_490d66(stream,iter)) return 0u;
    if (type==0u) return audio_pb_encode_bool_490e90(stream,iter);
    if (type>=1u && type<=3u) return audio_pb_encode_int_490eae(stream,iter);
    if (type==4u || type==5u) return audio_pb_encode_fixed_490f72(stream,iter);
    if (type==6u) return audio_pb_encode_bytes_490fa2(stream,iter);
    if (type==7u) return audio_pb_encode_string_490fe4(stream,iter);
    if (type==8u || type==9u) return audio_pb_encode_submessage_49104c(stream,iter);
    if (type==11u) return audio_pb_encode_fixed_length_bytes_4910e8(stream,iter);
    if (stream->errmsg==0) stream->errmsg=pb_invalid_field_type;
    return 0u;
}
