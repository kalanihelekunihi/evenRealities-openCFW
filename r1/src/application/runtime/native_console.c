/* Stock tokenizer 0x4f260 and RTT poll 0x88424. Command registration and
 * dispatch remain a separate source dependency. */
#include <stdint.h>
#include <string.h>
#include "SEGGER_RTT.h"
extern uint8_t *r1_native_strtok(uint8_t *,const uint8_t *);
extern void r1_eat_command_dispatch(char *,char *);
char r1_rtt_console_buffer[128]
 __attribute__((section(".bss.r1.rtt.console"),aligned(4)));
/* Stock 0x3e00e: channel-zero callback installed by the TX registry. */
uint32_t r1_rtt_channel0_write_callback(const void *buffer,uint32_t length)
{
    return SEGGER_RTT_Write(0,buffer,length);
}
void r1_eat_command_tokenize(void *input)
{
    char fields[2][128];
    uint8_t delimiters[4]={'=',0,0,0};
    memset(fields,0,sizeof(fields));
    uint8_t *token=r1_native_strtok(input,delimiters);
    for(unsigned i=0;token && i<2;++i){
        /* Stock's fixed snprintf("%s") result: at most 127 token bytes.
         * The zeroed final byte supplies termination for a truncated token. */
        for(unsigned n=0;n<127 && token[n];++n)fields[i][n]=(char)token[n];
        /* Stock fetches the next token even after filling the second field. */
        token=r1_native_strtok(NULL,delimiters);
    }
    r1_eat_command_dispatch(fields[0],fields[1]);
}
void r1_rtt_console_poll(void)
{
    unsigned count=SEGGER_RTT_Read(0,r1_rtt_console_buffer,127);
    if(count){
        /* Native drops the final received byte, regardless of its value. */
        r1_rtt_console_buffer[count-1]=0;
        r1_eat_command_tokenize(r1_rtt_console_buffer);
    }
}
