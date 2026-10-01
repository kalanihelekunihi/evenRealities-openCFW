/* Host check: emitted vectors are compared against original-code traces. */
#include "ring_protocol.h"
#include <assert.h>
#include <stdio.h>
static void emit(const char *name,const uint8_t *p,size_t n) {
    printf("%s ",name);for(size_t i=0;i<n;i++)printf("%02x",p[i]);puts("");
}
int main(void) {
    uint8_t b[16]={0};size_t n;
    n=g2_ring_heartbeat(b);emit("encode_472244_[]",b,n);
    n=g2_ring_report_interval(b,0x1234);emit("public_interval_path_big_endian",b,n);
    n=g2_ring_touch_enable(b,false);emit("encode_472378_[0]",b,n);
    n=g2_ring_touch_enable(b,true);emit("encode_472378_[1]",b,n);
    n=g2_ring_glasses_flags(b,false,false);emit("encode_4723d6_[0, 0]",b,n);
    n=g2_ring_glasses_flags(b,true,false);emit("encode_4723d6_[1, 0]",b,n);
    n=g2_ring_glasses_flags(b,false,true);emit("encode_4723d6_[0, 1]",b,n);
    n=g2_ring_glasses_flags(b,true,true);emit("encode_4723d6_[1, 1]",b,n);
    n=g2_ring_command_88(b);emit("encode_472546_[]",b,n);
    b[2]=0x61;
    assert(!g2_ring_rx_has_required_bytes(NULL,11));
    assert(!g2_ring_rx_has_required_bytes(b,2));
    assert(g2_ring_rx_has_required_bytes(b,7));
    for(n=8;n<11;n++)assert(!g2_ring_rx_has_required_bytes(b,n));
    assert(g2_ring_rx_has_required_bytes(b,11));
    b[7]=0x78;b[8]=0x56;b[9]=0x34;b[10]=0x12;
    assert(g2_ring_touch_tick_le(b)==0x12345678);
    b[2]=0x8b;assert(!g2_ring_rx_has_required_bytes(b,5));assert(g2_ring_rx_has_required_bytes(b,6));
    return 0;
}
