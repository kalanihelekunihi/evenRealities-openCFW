/* Native Cordio WsfOsSetNextHandler 0x52b980, 64-byte OS task state. */
#include <stdint.h>
extern uint8_t audio_wsf_task_state[0x40u]; /* RAM 0x20073230 */
uint8_t WsfOsSetNextHandler(void (*handler)(void)) {
    uint8_t index=audio_wsf_task_state[0x3du];
    audio_wsf_task_state[0x3du]=(uint8_t)(index+1u);
    ((void (**)(void))(void *)audio_wsf_task_state)[index]=handler;
    return index;
}
