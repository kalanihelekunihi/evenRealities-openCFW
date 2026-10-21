/* Native nanopb field dispatcher 0x490b1e, with authenticated error literal.
 * Child encoder contracts remain real imports until their bodies are reduced.
 */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state;
    uint32_t max_size,bytes_written;
    const char *errmsg;
};
struct pb_field_iter_candidate {
    const void *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size;
    const void *submessage_descriptor;
};
extern uint32_t audio_pb_field_is_default_49087a(const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_first_char_nonzero_490678(const void *);
extern uint32_t audio_pb_encode_callback_490aea(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_repeated_490690(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_single_490a46(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
static const char pb_missing_required_field[]="missing required field"; /* ROM 0x779fc4 */
uint32_t audio_pb_encode_field_490b1e(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    uint8_t type=iter->type;
    if ((type&0x30u)==0x30u) {
        if (*(const uint16_t *)iter->size!=iter->tag) return 1u;
    } else if ((type&0x30u)==0x10u) {
        if (iter->size==0) {
            if ((type&0xc0u)==0u && audio_pb_field_is_default_49087a(iter)) return 1u;
        } else if (!audio_pb_first_char_nonzero_490678(iter->size)) return 1u;
    }
    if (iter->data==0) {
        if ((type&0x30u)==0u) {
            if (stream->errmsg==0) stream->errmsg=pb_missing_required_field;
            return 0u;
        }
        return 1u;
    }
    if ((type&0xc0u)==0x40u) return audio_pb_encode_callback_490aea(stream,iter);
    if ((type&0x30u)==0x20u) return audio_pb_encode_repeated_490690(stream,iter);
    return audio_pb_encode_single_490a46(stream,iter);
}
