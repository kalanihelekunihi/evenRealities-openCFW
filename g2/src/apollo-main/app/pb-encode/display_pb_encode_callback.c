/* Native nanopb callback dispatch 0x490aea and first-char predicate 0x490678. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
struct pb_msgdesc_candidate {
    const uint32_t *field_info; const void *submsg_info,*default_value;
    uint32_t (*field_callback)(void *,struct pb_ostream_candidate *);
};
struct pb_field_iter_candidate {
    const struct pb_msgdesc_candidate *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size; const void *submessage_descriptor;
};
static const char pb_callback_error[]="callback error"; /* ROM 0x787cf0 via 0x4910c4 */
uint32_t audio_pb_encode_callback_490aea(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    if (iter->descriptor->field_callback==0 || iter->descriptor->field_callback(0,stream)) return 1u;
    if (stream->errmsg==0) stream->errmsg=pb_callback_error;
    return 0u;
}
uint32_t audio_pb_first_char_nonzero_490678(const void *value)
{
    return *(const uint8_t *)value!=0u;
}
