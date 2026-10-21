/* Nanopb native 0x4d94ba begin, 0x4d9384 reset, 0x4d93d8 next. */
#include <stddef.h>
#include <stdint.h>
struct pb_field_iter_candidate {
    const void *descriptor;void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size;
    uint8_t type;
    void *field,*data,*size;
    const void *submessage_descriptor;
};
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native ARM nanopb iterator size");
_Static_assert(offsetof(struct pb_field_iter_candidate,type)==22u,"native ARM type offset");
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_pb_iter_decode_field_4d916e(struct pb_field_iter_candidate *);
extern void audio_pb_iter_advance_4d930a(struct pb_field_iter_candidate *);
static uint32_t iter_reset(struct pb_field_iter_candidate *iterator,const void *descriptor,const void *message)
{
    audio_uart_buffer_zero(iterator,40u,0u);
    iterator->descriptor=descriptor;
    iterator->message=(void *)message;
    return audio_pb_iter_decode_field_4d916e(iterator);
}
uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *iterator,const void *descriptor,const void *message)
{
    /* Native 0x4d94b8 forwards message unchanged before reset. */
    return iter_reset(iterator,descriptor,message);
}
uint32_t audio_pb_iter_next_4d93d8(struct pb_field_iter_candidate *iterator)
{
    audio_pb_iter_advance_4d930a(iterator);
    (void)audio_pb_iter_decode_field_4d916e(iterator);
    return iterator->index!=0u;
}
