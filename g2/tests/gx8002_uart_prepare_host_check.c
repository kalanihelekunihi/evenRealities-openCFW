/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <string.h>
#include "prepare.c"
UART_MSG_REGIST s_uart_msg_regist_array[16];
int main(void) {
    unsigned char buffer[128];
    for (unsigned index=0; index<16; ++index)
    for (unsigned flags=0; flags<2; ++flags)
    for (unsigned offset=0; offset<4; ++offset) {
        MSG_PACK packet={0};
        memset(s_uart_msg_regist_array,0,sizeof s_uart_msg_regist_array);
        packet.msg_header.cmd=0x101; packet.msg_header.flags=flags;
        packet.msg_header.length=20; packet.len=99;
        UART_MSG_REGIST *entry=&s_uart_msg_regist_array[index];
        entry->msg_id=0x101; entry->msg_buffer=buffer;
        entry->msg_buffer_length=64; entry->msg_buffer_offset=offset*20;
        unsigned start=offset*20+20>64 ? 0 : offset*20;
        assert(_UartMessagePrepareRecv(&packet)==0);
        assert(packet.body_addr==buffer+start);
        assert(entry->msg_buffer_offset==start+20-(flags?4:0));
    }
    for (unsigned reason=0; reason<3; ++reason) {
        MSG_PACK packet={0};
        memset(s_uart_msg_regist_array,0,sizeof s_uart_msg_regist_array);
        packet.msg_header.cmd=0x101;packet.msg_header.length=20;
        packet.body_addr=buffer;packet.len=99;
        if (reason!=0) {
            s_uart_msg_regist_array[0].msg_id=0x101;
            s_uart_msg_regist_array[0].msg_buffer_length=reason==1?4:64;
            s_uart_msg_regist_array[0].msg_buffer=reason==1?buffer:0;
        }
        assert(_UartMessagePrepareRecv(&packet)==-1);
        assert(packet.body_addr==0 && packet.len==0);
    }
    /* The first matching command owns the decision, even if unusable. */
    for (unsigned bad=0; bad<2; ++bad) {
        MSG_PACK packet={0};
        memset(s_uart_msg_regist_array,0,sizeof s_uart_msg_regist_array);
        packet.msg_header.cmd=0x101;packet.msg_header.length=20;
        for (unsigned i=0;i<2;++i) {
            s_uart_msg_regist_array[i].msg_id=0x101;
            s_uart_msg_regist_array[i].msg_buffer=buffer;
            s_uart_msg_regist_array[i].msg_buffer_length=64;
        }
        if (bad) s_uart_msg_regist_array[0].msg_buffer=0;
        else s_uart_msg_regist_array[0].msg_buffer_length=4;
        assert(_UartMessagePrepareRecv(&packet)==-1);
        assert(packet.body_addr==0 && s_uart_msg_regist_array[1].msg_buffer_offset==0);
    }
    /* Trailer affects required capacity, but the wrap check uses total length. */
    {
        MSG_PACK packet={0};
        memset(s_uart_msg_regist_array,0,sizeof s_uart_msg_regist_array);
        packet.msg_header.cmd=0x101;packet.msg_header.length=20;packet.msg_header.flags=1;
        s_uart_msg_regist_array[0]=(UART_MSG_REGIST){.msg_id=0x101,.msg_buffer=buffer,
            .msg_buffer_length=32,.msg_buffer_offset=16};
        assert(_UartMessagePrepareRecv(&packet)==0);
        assert(packet.body_addr==buffer && s_uart_msg_regist_array[0].msg_buffer_offset==16);
    }
    for (unsigned length=0;length<4;++length) {
        MSG_PACK packet={0};
        memset(s_uart_msg_regist_array,0,sizeof s_uart_msg_regist_array);
        packet.msg_header.cmd=0x101;packet.msg_header.length=length;packet.msg_header.flags=1;
        s_uart_msg_regist_array[0]=(UART_MSG_REGIST){.msg_id=0x101,.msg_buffer=buffer,.msg_buffer_length=64};
        assert(_UartMessagePrepareRecv(&packet)==-1);
        assert(packet.body_addr==0 && packet.len==0);
    }
    return 0;
}
