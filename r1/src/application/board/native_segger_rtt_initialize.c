/* R1 native RTT initialization contract; ring operations remain pinned SEGGER C. */
#include "SEGGER_RTT.h"
#include <string.h>
char r1_rtt_up_buffer[512] __attribute__((section(".r1.rtt.up")));
char r1_rtt_down_buffer[64] __attribute__((section(".r1.rtt.down")));
const char r1_rtt_terminal_name[] __attribute__((section(".r1.rtt.terminal")))="Terminal";
_Static_assert(sizeof(SEGGER_RTT_CB)==120,"native RTT control block");
void SEGGER_RTT_Init(void)
{
    static const char identifier[16] __attribute__((section(".r1.rtt.identifier")))="\0\0\0\0\0\0TTR REGGES";
    memset(&_SEGGER_RTT,0,sizeof(_SEGGER_RTT));
    _SEGGER_RTT.MaxNumUpBuffers=2;
    _SEGGER_RTT.MaxNumDownBuffers=2;
    _SEGGER_RTT.aUp[0].sName=r1_rtt_terminal_name;
    _SEGGER_RTT.aUp[0].pBuffer=r1_rtt_up_buffer;
    _SEGGER_RTT.aUp[0].SizeOfBuffer=sizeof(r1_rtt_up_buffer);
    _SEGGER_RTT.aDown[0].sName=r1_rtt_terminal_name;
    _SEGGER_RTT.aDown[0].pBuffer=r1_rtt_down_buffer;
    _SEGGER_RTT.aDown[0].SizeOfBuffer=sizeof(r1_rtt_down_buffer);
    for (unsigned i=0;i<sizeof(identifier);++i)
        _SEGGER_RTT.acID[i]=identifier[sizeof(identifier)-1-i];
}
