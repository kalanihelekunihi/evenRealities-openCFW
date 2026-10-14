/* Apollo NEMA blit descriptor 0x4b1608..0x4b178b. Candidate. */
#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[1]; /* selected */
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t); /* selected */

static uint32_t align4_native(uint32_t value) {
    uint32_t x=value+3u;
    return (x+((uint32_t)((int32_t)x>>1)>>30))&~3u;
}
static uint32_t align2_native(uint32_t value) {
    uint32_t x=value+1u;
    return (x+(x>>31))&~1u;
}
static uint32_t divide8_native(uint32_t value) {
    uint32_t x=value+7u;
    return (uint32_t)((int32_t)(x+((uint32_t)((int32_t)x>>2)>>29))>>3);
}
void display_driver_gpu_blit_4b1608(void *source,uint32_t width,uint32_t height,
                                    uint32_t format,uint32_t stride,uint32_t flags) {
    volatile uint32_t *ctx=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    if(stride==UINT32_MAX) {
        uint32_t kind=format&0x7fu;
        stride=width;
        if((flags&0x10u)!=0u) stride=align4_native(stride);
        if(kind==0x12u||kind==0x16u||kind==0x17u||kind==0x4eu)
            stride=align4_native(stride);
        if(kind==0x4cu||kind==0x4du) stride=align2_native(stride);
        switch(kind) {
        case 0x0bu:case 0x0cu:case 0x27u:case 0x2au:
            stride=divide8_native(stride);break;
        case 0x12u:stride<<=1;break;
        case 0x16u:case 0x17u:case 0x4cu:case 0x4du:case 0x4eu:
            stride*=3u;break;
        case 0x28u:case 0x2bu:case 0x30u:case 0x31u:
            stride=divide8_native(stride*2u);break;
        case 0x29u:case 0x2cu:case 0x34u:case 0x35u:
            stride=divide8_native(stride*4u);break;
        default: {
            uint32_t bytes=4u;
            switch(kind) {
            case 4u:case 5u:case 6u:case 0x0du:case 0x13u:case 0x1du:
            case 0x3du:case 0x3eu:case 0x3fu:case 0x44u:
            case 0x46u:case 0x47u:case 0x48u:case 0x49u:
            case 0x4au:case 0x4bu:case 0x4cu:case 0x4du:
                bytes=2u;break;
            case 7u:case 8u:case 9u:case 0x18u:case 0x19u:case 0x1au:
            case 0x28u:case 0x30u:case 0x31u:case 0x38u:
            case 0x40u:case 0x41u:case 0x42u:case 0x43u:case 0x45u:
                bytes=1u;break;
            case 0x39u:case 0x3cu:bytes=3u;break;
            default:break;
            }
            stride*=bytes;break;
        }
        }
    }
    uint32_t descriptor=(stride&0xffffu)|(flags<<16)|(format<<24);
    ctx[0x5cu/4u]=descriptor;
    ctx[0x50u/4u]=(uint32_t)(uintptr_t)source;
    ctx[0x54u/4u]=width;
    ctx[0x58u/4u]=height;
    ctx[0x60u/4u]=1u;
    ctx[0x64u/4u]=format;
    uint32_t *command=audio_uart_nema_cl_get_space_514aec(3u);
    if(command!=0) {
        command[0]=0x10u;
        command[1]=(uint32_t)(uintptr_t)source;
        command[2]=0x14u;
        command[3]=ctx[0x5cu/4u];
        command[4]=0x18u;
        command[5]=width|(height<<16);
    }
}
