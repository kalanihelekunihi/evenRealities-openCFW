/* Native nanopb static-storage field decoder 0x48f968. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_msgdesc_candidate { const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;const uint8_t *default_value;void *field_callback;uint16_t field_count,required_field_count,largest_tag; };
struct pb_field_iter_candidate { const struct pb_msgdesc_candidate *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const struct pb_msgdesc_candidate *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_decode_scalar_48f7f4(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_substream_begin_48f77e(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_substream_end_48f7ca(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_default_fields_48fdf2(struct pb_field_iter_candidate *);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
static const char pb_array_overflow[]="array overflow"; /* ROM 0x787cb0 */
static const char pb_failed_defaults[]="failed to set defaults"; /* ROM 0x779f7c */
static const char pb_invalid_field_type[]="invalid field type"; /* ROM 0x7817f0 */

uint32_t audio_pb_decode_static_field_48f968(struct pb_istream_candidate *s,uint32_t wire,struct pb_field_iter_candidate *it)
{
    uint32_t count_mode=it->type&0x30u;
    uint16_t *count;
    if (count_mode==0u) return audio_pb_decode_scalar_48f7f4(s,(uint8_t)wire,it);
    if (count_mode==0x10u) {
        if (it->size!=0) *(uint8_t *)it->size=1u;
        return audio_pb_decode_scalar_48f7f4(s,(uint8_t)wire,it);
    }
    if (count_mode==0x20u) {
        count=(uint16_t *)it->size;
        it->data=(uint8_t *)it->field+(uint32_t)(*count)*it->data_size;
        if ((uint8_t)wire==2u && (it->type&15u)<6u) {
            struct pb_istream_candidate sub;
            uint32_t ok=1u;
            if (!audio_pb_substream_begin_48f77e(s,&sub)) return 0u;
            while (sub.bytes_left!=0u && *count<it->array_size) {
                if (!audio_pb_decode_scalar_48f7f4(&sub,255u,it)) { ok=0u;break; }
                ++*count;
                it->data=(uint8_t *)it->data+it->data_size;
            }
            if (sub.bytes_left!=0u) {
                if (s->errmsg==0) s->errmsg=pb_array_overflow;
                return 0u;
            }
            if (!audio_pb_substream_end_48f7ca(s,&sub)) return 0u;
            return ok;
        }
        {
            uint16_t old=*count;
            *count=(uint16_t)(old+1u);
            if (old<it->array_size) return audio_pb_decode_scalar_48f7f4(s,(uint8_t)wire,it);
            if (s->errmsg==0) s->errmsg=pb_array_overflow;
            return 0u;
        }
    }
    if (count_mode==0x30u) {
        uint16_t *selector=(uint16_t *)it->size;
        if (((it->type&15u)==8u || (it->type&15u)==9u) && *selector!=it->tag) {
            const struct pb_msgdesc_candidate *desc=it->submessage_descriptor;
            audio_uart_buffer_zero(it->data,it->data_size,0u);
            if ((desc->default_value!=0 || desc->field_callback!=0 ||
                 *desc->submsg_info!=0)) {
                struct pb_field_iter_candidate nested;
                if (audio_pb_iter_begin_4d94ba(&nested,desc,it->data)!=0u &&
                    !audio_pb_default_fields_48fdf2(&nested)) {
                    if (s->errmsg==0) s->errmsg=pb_failed_defaults;
                    return 0u;
                }
            }
        }
        *selector=it->tag;
        return audio_pb_decode_scalar_48f7f4(s,(uint8_t)wire,it);
    }
    if (s->errmsg==0) s->errmsg=pb_invalid_field_type;
    return 0u;
}
