/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <string.h>
#include "header.c"
static unsigned calls;
unsigned int open_cfw_gx8002_crc32(unsigned int seed, const unsigned char *data, unsigned int length)
{
    assert(seed == 0 && length == 10 && data != 0);
    ++calls;
    return 0x12345678;
}
int main(void)
{
    for (unsigned port=0; port<2; ++port) {
        for (unsigned split=0; split<=10; ++split) {
            MESSAGE_HEADER header;
            memset(&header,0,sizeof header);
            unsigned char input[10]={1,2,3,4,5,6,0x78,0x56,0x34,0x12};
            unsigned char *cursor=input;
            unsigned remaining=split;
            unsigned prior=calls;
            int result=open_cfw_gx8002_uart_header_probe(port,&header,&cursor,&remaining);
            assert(remaining==0);
            if (split<10) {
                assert(result==0 && calls==prior);
                cursor=input+split; remaining=10-split;
                result=open_cfw_gx8002_uart_header_probe(port,&header,&cursor,&remaining);
            }
            assert(result==1 && remaining==0 && calls==prior+1);
            assert(memcmp((unsigned char *)&header+4,input,10)==0);
        }
    }
    for (unsigned port=0; port<2; ++port) {
        for (unsigned bad=0; bad<2; ++bad) {
            MESSAGE_HEADER header;
            memset(&header,0xa5,sizeof header);
            unsigned char input[13]={1,2,3,4,5,6,0x78,0x56,0x34,0x12,0xde,0xad,0xbe};
            if (bad) input[9] ^= 1;
            unsigned char *cursor=input;
            unsigned remaining=sizeof input;
            unsigned prior=calls;
            int result=open_cfw_gx8002_uart_header_probe(port,&header,&cursor,&remaining);
            assert(result==(bad ? -1 : 1));
            assert(remaining==3 && cursor==input+10 && calls==prior+1);
            assert(input[10]==0xde && input[11]==0xad && input[12]==0xbe);
            assert(header.magic==(bad ? 0u : 0xa5a5a5a5u));
            /* CRC failure must reset the counter for the next header too. */
            input[9]=0x12; cursor=input; remaining=10;
            result=open_cfw_gx8002_uart_header_probe(port,&header,&cursor,&remaining);
            assert(result==1 && remaining==0 && calls==prior+2);
        }
    }
    return 0;
}
