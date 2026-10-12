/* Native nanopb submessage decoder 0x49048c, including typed callback slot. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_msgdesc_candidate { const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;const uint8_t *default_value;void *field_callback;uint16_t field_count,required_field_count,largest_tag; };
struct pb_field_iter_candidate { const struct pb_msgdesc_candidate *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const struct pb_msgdesc_candidate *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_substream_begin_48f77e(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_substream_end_48f7ca(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_decode_parent_48fe98(struct pb_istream_candidate *,const void *,void *,uint32_t);
static const char pb_invalid_descriptor[]="invalid field descriptor"; /* ROM 0x76f454 */

uint32_t audio_pb_decode_submessage_49048c(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    struct pb_istream_candidate sub;
    uint32_t result=1u;
    uint32_t callback_consumed=0u;
    if (!audio_pb_substream_begin_48f77e(s,&sub)) return 0u;
    if (it->submessage_descriptor==0) {
        if (s->errmsg==0) s->errmsg=pb_invalid_descriptor;
        return 0u;
    }
    if ((it->type&15u)==9u && it->size!=0) {
        uint8_t *context=(uint8_t *)it->size;
        uint32_t (*callback)(struct pb_istream_candidate *,struct pb_field_iter_candidate *,void *)=
            *(uint32_t (**)(struct pb_istream_candidate *,struct pb_field_iter_candidate *,void *))(void *)(context-8);
        if (callback!=0) {
            result=callback(&sub,it,context-4);
            if (sub.bytes_left==0u) callback_consumed=1u;
        }
    }
    if (result!=0u && callback_consumed==0u) {
        uint32_t flags=0u;
        if ((it->type&0xc0u)==0u && (it->type&0x30u)!=0x20u) flags=1u;
        result=audio_pb_decode_parent_48fe98(&sub,it->submessage_descriptor,it->data,flags);
    }
    if (!audio_pb_substream_end_48f7ca(s,&sub)) result=0u;
    return result&255u;
}
