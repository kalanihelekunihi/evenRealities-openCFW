/* Native pb_decode 0x490120: explicit flags=0 and byte return. */
#include <stdint.h>
extern uint32_t audio_pb_decode_parent_48fe98(void *,const void *,void *,uint32_t);
uint32_t audio_uart_pb_decode(void *stream,const void *descriptor,void *message)
{
    return audio_pb_decode_parent_48fe98(stream,descriptor,message,0u)&255u;
}
