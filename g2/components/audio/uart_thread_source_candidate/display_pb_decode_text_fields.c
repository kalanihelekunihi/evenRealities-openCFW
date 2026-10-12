/* Native nanopb bytes/string/fixed-bytes readers 0x490358, 0x4903ea,
 * 0x49053c. Their exact bounded storage and error behavior is retained.
 */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_field_iter_candidate { const void *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const void *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_read_varint_48f4b8(struct pb_istream_candidate *,uint32_t *,uint8_t *);
extern uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *,void *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
static const char pb_size_too_large[]="size too large"; /* ROM 0x787c90 */
static const char pb_no_malloc_support[]="no malloc support"; /* ROM 0x781804 */
static const char pb_bytes_overflow[]="bytes overflow"; /* ROM 0x787cd0 */
static const char pb_string_overflow[]="string overflow"; /* ROM 0x787ce0 */
static const char pb_fixed_size[]="incorrect fixed length bytes size"; /* ROM 0x75768c */
static void set_error(struct pb_istream_candidate *s,const char *p) { if (s->errmsg==0) s->errmsg=p; }

uint32_t audio_pb_decode_bytes_490358(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    uint32_t n;
    if (!audio_pb_read_varint_48f4b8(s,&n,0)) return 0u;
    if (n>=65536u || n+2u<n) { set_error(s,n>=65536u?pb_bytes_overflow:pb_size_too_large);return 0u; }
    if ((it->type&0xc0u)==0x80u) { set_error(s,pb_no_malloc_support);return 0u; }
    if (it->data_size<n+2u) { set_error(s,pb_bytes_overflow);return 0u; }
    *(uint16_t *)it->data=(uint16_t)n;
    return audio_pb_read_stream_48f3be(s,(uint8_t *)it->data+2,n);
}
uint32_t audio_pb_decode_string_4903ea(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    uint32_t n;
    if (!audio_pb_read_varint_48f4b8(s,&n,0)) return 0u;
    if (n==UINT32_MAX || n+1u<n) { set_error(s,pb_size_too_large);return 0u; }
    if ((it->type&0xc0u)==0x80u) { set_error(s,pb_no_malloc_support);return 0u; }
    if (it->data_size<n+1u) { set_error(s,pb_string_overflow);return 0u; }
    ((uint8_t *)it->data)[n]=0u;
    return audio_pb_read_stream_48f3be(s,it->data,n);
}
uint32_t audio_pb_decode_extension_49053c(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    uint32_t n;
    if (!audio_pb_read_varint_48f4b8(s,&n,0)) return 0u;
    if (n>=65536u) { set_error(s,pb_bytes_overflow);return 0u; }
    if (n==0u) { audio_uart_buffer_zero(it->data,it->data_size,0u);return 1u; }
    if (n==it->data_size) return audio_pb_read_stream_48f3be(s,it->data,it->data_size);
    set_error(s,pb_fixed_size);
    return 0u;
}
