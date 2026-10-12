/* Native stack state-one block assembly 0x5364a4 and exact XOR16 helper
 * 0x542a60. The source uses the already selected SecLeEncryptCmd provider
 * for the native 0x5363ae child. */
#include <stdint.h>

extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void SecLeEncryptCmd(const uint8_t *,const uint8_t *,void *,uint8_t);

void audio_ble_stack_xor16_542a60(uint8_t *destination,const uint8_t *source)
{
    for (uint32_t i=0u;i<16u;++i) destination[i]^=source[i];
}

void audio_ble_stack_state1_5364a4(uint8_t *message)
{
    uint32_t context_word;
    __builtin_memcpy(&context_word,message+0x30u,4u);
    uint8_t *context=(uint8_t *)(uintptr_t)context_word;
    uint32_t data_word;
    __builtin_memcpy(&data_word,context,4u);
    uint8_t *data=(uint8_t *)(uintptr_t)data_word;
    uint16_t offset=(uint16_t)context[0x24u]|((uint16_t)context[0x25u]<<8);
    int16_t remaining=(int16_t)((int16_t)((uint16_t)context[0x26u]|
                       ((uint16_t)context[0x27u]<<8))-(int16_t)offset);
    uint8_t block[16];
    if (remaining<17) {
        (void)audio_queue_copy_bytes(block,data+offset,(uint32_t)(int32_t)remaining);
        if (remaining!=16) {
            audio_uart_buffer_zero(block+remaining,(uint32_t)(16-remaining),0u);
            block[remaining]=0x80u;
        }
        audio_ble_stack_xor16_542a60(block,context+0x14u);
        context[0x29u]=2u;
    } else {
        (void)audio_queue_copy_bytes(block,data+offset,16u);
    }
    if (offset!=0u) audio_ble_stack_xor16_542a60(block,message+16u);
    offset=(uint16_t)(offset+16u);
    context[0x24u]=(uint8_t)offset;
    context[0x25u]=(uint8_t)(offset>>8);
    SecLeEncryptCmd(context+4u,block,message,context[0x28u]);
}
