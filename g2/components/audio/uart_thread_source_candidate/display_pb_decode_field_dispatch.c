/* Native nanopb field allocation/encoding-mode dispatch 0x48fbe4. */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state;uint32_t bytes_left;const char *errmsg;
};
struct pb_field_iter_candidate {
    const void *descriptor;void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size;
    uint8_t type;
    void *field,*data,*size;
    const void *submessage_descriptor;
};
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_decode_static_field_48f968(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_callback_field_48fb30(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_pointer_field_48fb1c(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
static const char pb_invalid_field_type[]="invalid field type"; /* ROM 0x7817f0 */
uint32_t audio_pb_decode_field_48fbe4(struct pb_istream_candidate *s,uint32_t wire,struct pb_field_iter_candidate *iter)
{
    switch (iter->type&0xc0u) {
    case 0u:return audio_pb_decode_static_field_48f968(s,wire,iter);
    case 0x40u:return audio_pb_decode_callback_field_48fb30(s,wire,iter);
    case 0x80u:return audio_pb_decode_pointer_field_48fb1c(s,wire,iter);
    default:
        if (s->errmsg==0) s->errmsg=pb_invalid_field_type;
        return 0u;
    }
}
