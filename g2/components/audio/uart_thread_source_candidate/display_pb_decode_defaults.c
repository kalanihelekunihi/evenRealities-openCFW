/* Native nanopb field and iterator default initialization 0x48fce2/0x48fdf2. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_msgdesc_candidate { const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;const uint8_t *default_value;void *field_callback;uint16_t field_count,required_field_count,largest_tag; };
struct pb_field_iter_candidate { const struct pb_msgdesc_candidate *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const struct pb_msgdesc_candidate *submessage_descriptor; };
struct pb_extension_candidate { const void *type;void *dest;struct pb_extension_candidate *next;uint32_t found; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_extension_iter_4d93a4(struct pb_field_iter_candidate *,const struct pb_extension_candidate *);
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_iter_next_4d93d8(struct pb_field_iter_candidate *);
extern uint32_t audio_pb_read_tag_48f66c(struct pb_istream_candidate *,uint8_t *,uint32_t *,uint8_t *);
extern uint32_t audio_pb_decode_field_48fbe4(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
extern void audio_uart_pb_stream_init(struct pb_istream_candidate *,const void *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
uint32_t audio_pb_default_fields_48fdf2(struct pb_field_iter_candidate *);

uint32_t audio_pb_default_field_48fce2(struct pb_field_iter_candidate *it)
{
    uint8_t type=it->type;
    if ((type&15u)==10u) {
        struct pb_extension_candidate *ext=*(struct pb_extension_candidate **)it->data;
        for (;ext!=0;ext=ext->next) {
            struct pb_field_iter_candidate nested;
            if (audio_pb_extension_iter_4d93a4(&nested,ext)) {
                ext->found=0u;
                if (!audio_pb_default_fields_48fdf2(&nested)) return 0u;
            }
        }
    } else if ((type&0xc0u)==0u) {
        uint32_t initialize=1u;
        if ((type&0x30u)==0x10u && it->size!=0) *(uint8_t *)it->size=0u;
        else if ((type&0x30u)==0x20u || (type&0x30u)==0x30u) {
            *(uint16_t *)it->size=0u;
            initialize=0u;
        }
        if (initialize) {
            if (((type&15u)==8u || (type&15u)==9u) &&
                (it->submessage_descriptor->default_value!=0 ||
                 it->submessage_descriptor->field_callback!=0 ||
                 *it->submessage_descriptor->submsg_info!=0)) {
                struct pb_field_iter_candidate nested;
                if (audio_pb_iter_begin_4d94ba(&nested,it->submessage_descriptor,it->data) &&
                    !audio_pb_default_fields_48fdf2(&nested)) return 0u;
            } else audio_uart_buffer_zero(it->data,it->data_size,0u);
        }
    } else if ((type&0xc0u)==0x80u) {
        *(void **)it->field=0;
        if ((type&0x30u)==0x20u || (type&0x30u)==0x30u) *(uint16_t *)it->size=0u;
    }
    return 1u;
}

uint32_t audio_pb_default_fields_48fdf2(struct pb_field_iter_candidate *it)
{
    struct pb_istream_candidate stream={0};
    uint8_t wire=0u,eof=0u;
    uint32_t tag=0u;
    if (it->descriptor->default_value!=0) {
        audio_uart_pb_stream_init(&stream,it->descriptor->default_value,UINT32_MAX);
        if (!audio_pb_read_tag_48f66c(&stream,&wire,&tag,&eof)) return 0u;
    }
    do {
        if (!audio_pb_default_field_48fce2(it)) return 0u;
        if (tag!=0u && it->tag==tag) {
            if (!audio_pb_decode_field_48fbe4(&stream,wire,it)) return 0u;
            if (!audio_pb_read_tag_48f66c(&stream,&wire,&tag,&eof)) return 0u;
            if (it->size!=0) *(uint8_t *)it->size=0u;
        }
    } while (audio_pb_iter_next_4d93d8(it));
    return 1u;
}
