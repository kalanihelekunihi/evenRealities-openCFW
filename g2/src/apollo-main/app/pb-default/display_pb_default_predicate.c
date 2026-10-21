/* Nanopb default predicate 0x49087a and callback marker 0x4d94e6. */
#include <stdint.h>
struct pb_field_iter_candidate;
struct pb_msgdesc_candidate {
    const uint32_t *field_info; const void *submsg_info,*default_value;
    uint32_t (*field_callback)(void *,void *,const struct pb_field_iter_candidate *);
};
struct pb_field_iter_candidate {
    const struct pb_msgdesc_candidate *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size; const void *submessage_descriptor;
};
extern uint32_t audio_pb_first_char_nonzero_490678(const void *);
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_iter_next_4d93d8(struct pb_field_iter_candidate *);
uint32_t audio_pb_default_callback_4d94e6(void *input,void *output,const struct pb_field_iter_candidate *iter)
{
    if (iter->data_size==8u && iter->data!=0) {
        const uintptr_t *callback=(const uintptr_t *)iter->data;
        if (callback[0]!=0u) {
            uint32_t (*fn)(void *,const struct pb_field_iter_candidate *,const void *)=(void *)callback[0];
            if (input!=0) return fn(input,iter,callback+1);
            if (output!=0) return fn(output,iter,callback+1);
        }
    }
    return 1u;
}
uint32_t audio_pb_field_is_default_49087a(const struct pb_field_iter_candidate *iter)
{
    uint8_t type=iter->type;
    if ((type&0xc0u)==0u) {
        if ((type&0x30u)==0u) return 0u;
        if ((type&0x30u)==0x20u || (type&0x30u)==0x30u)
            return *(const uint16_t *)iter->size==0u;
        if ((type&0x30u)==0x10u && iter->size!=0)
            return !audio_pb_first_char_nonzero_490678(iter->size);
        if (iter->descriptor->default_value!=0) return 0u;
        if ((type&15u)<6u) {
            for (uint16_t i=0;i<iter->data_size;i++)
                if (((const uint8_t *)iter->data)[i]!=0u) return 0u;
            return 1u;
        }
        if ((type&15u)==6u) return *(const uint16_t *)iter->data==0u;
        if ((type&15u)==7u) return *(const uint8_t *)iter->data==0u;
        if ((type&15u)==11u) return iter->data_size==0u;
        if ((type&15u)==8u || (type&15u)==9u) {
            struct pb_field_iter_candidate nested;
            if (!audio_pb_iter_begin_4d94ba(&nested,iter->submessage_descriptor,iter->data)) return 1u;
            do {
                if (!audio_pb_field_is_default_49087a(&nested)) return 0u;
            } while (audio_pb_iter_next_4d93d8(&nested));
            return 1u;
        }
    } else if ((type&0xc0u)==0x80u) {
        return iter->data==0;
    } else if ((type&0xc0u)==0x40u) {
        if ((type&15u)==10u) return *(const uintptr_t *)iter->data==0u;
        if (iter->descriptor->field_callback==audio_pb_default_callback_4d94e6)
            return *(const uintptr_t *)iter->data==0u;
        return iter->descriptor->field_callback==0;
    }
    return 0u;
}
