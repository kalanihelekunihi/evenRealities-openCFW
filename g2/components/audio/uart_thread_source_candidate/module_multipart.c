/* TinyFrame multipart wrappers 0x492200/0x49224c/0x492266/0x492278/
 * 0x492280. Native Thumb confirms the fifth halfword crosses each wrapper
 * on the stack. The begin/payload/close engines are explicit code children. */
#include <stdint.h>
extern uint32_t audio_uart_module_begin_core(void *,void *,void *,void *,
                                             uint16_t); /* 0x4920aa */
extern void audio_uart_module_payload_core(void *,const void *,uint32_t); /* 0x492114 */
extern void audio_uart_module_close_core(void *); /* 0x492198 */
uint32_t audio_uart_module_multipart_begin(void *module,void *frame,
                                            void *on_begin,void *on_end,
                                            uint32_t timeout) {
    uint8_t *f=(uint8_t *)frame;
    *(uint32_t *)(f+8u)=0u; /* 0x492266 makes this an open multipart */
    if(audio_uart_module_begin_core(module,frame,on_begin,on_end,
                                    (uint16_t)timeout)==0u) return 0u;
    uint16_t size=*(uint16_t *)(f+0xcu);
    const void *payload=*(const void **)(f+8u);
    if(size==0u || payload!=0) {
        audio_uart_module_payload_core(module,payload,size);
        audio_uart_module_close_core(module);
    }
    return 1u;
}
void audio_uart_module_multipart_payload(void *module,const void *payload,
                                          uint32_t length) {
    audio_uart_module_payload_core(module,payload,length);
}
void audio_uart_module_multipart_close(void *module) {
    audio_uart_module_close_core(module);
}
