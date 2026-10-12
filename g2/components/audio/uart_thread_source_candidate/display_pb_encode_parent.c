/* Nanopb 0.4-style pb_encode parent, native Main 0x490c32.
 * Iterator/field and extension encoders are real separate lower bodies. */
#include <stddef.h>
#include <stdint.h>
struct pb_field_iter_candidate {
    const void *descriptor;
    void *message;
    uint16_t index;
    uint16_t field_info_index;
    uint16_t required_field_index;
    uint16_t submessage_index;
    uint16_t tag;
    uint16_t data_size;
    uint16_t array_size;
    uint8_t type;
    void *field;
    void *data;
    void *size;
    const void *submessage_descriptor;
};
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native ARM nanopb iterator size");
_Static_assert(offsetof(struct pb_field_iter_candidate,type)==22u,"native ARM type offset");
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_iter_next_4d93d8(struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_extension_490bf8(void *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_field_490b1e(void *,struct pb_field_iter_candidate *);
uint32_t audio_pb_encode(void *stream,const void *descriptor,const void *message)
{
    struct pb_field_iter_candidate iterator;
    if (!audio_pb_iter_begin_4d94ba(&iterator,descriptor,message)) return 1u;
    do {
        uint32_t ok=((iterator.type&15u)==10u)
            ?audio_pb_encode_extension_490bf8(stream,&iterator)
            :audio_pb_encode_field_490b1e(stream,&iterator);
        if (!ok) return 0u;
    } while (audio_pb_iter_next_4d93d8(&iterator));
    return 1u;
}
