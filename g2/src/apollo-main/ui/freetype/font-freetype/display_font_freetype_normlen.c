/* Native FT_Vector_NormLen0x524902, pinned FreeType 2.9.1 ftcalc.c.
 * Explicit 32-bit wraps match the Cortex-M4 multiply/divide instructions. */
#include <stdint.h>
typedef struct {int32_t x,y;} Vector;
static uint32_t magnitude(int32_t v) {return v<0?0u-(uint32_t)v:(uint32_t)v;}
uint32_t audio_uart_font_vector_normlen(Vector *vector) {
    int32_t ox=vector->x,oy=vector->y;
    uint32_t x=magnitude(ox),y=magnitude(oy);
    if(x==0u) {if(y!=0u) vector->y=oy<0?-65536:65536;return y;}
    if(y==0u) {vector->x=ox<0?-65536:65536;return x;}
    uint32_t length=x>y?x+(y>>1u):y+(x>>1u);
    int32_t shift=(int32_t)__builtin_clz(length);
    shift-=15+(length>=(0xaaaaaaaau>>(uint32_t)shift));
    if(shift>0) {
        x<<=(uint32_t)shift;y<<=(uint32_t)shift;
        length=x>y?x+(y>>1u):y+(x>>1u);
    } else {
        x>>=(uint32_t)(-shift);y>>=(uint32_t)(-shift);
        length>>=(uint32_t)(-shift);
    }
    int32_t b=(int32_t)(65536u-length);
    uint32_t u=0,v=0;
    int32_t z;
    do {
        u=x+(uint32_t)((int32_t)((uint32_t)x*(uint32_t)b)>>16);
        v=y+(uint32_t)((int32_t)((uint32_t)y*(uint32_t)b)>>16);
        uint32_t square=u*u+v*v;
        z=((int32_t)square)/(-512);
        z=(int32_t)((uint32_t)z*(uint32_t)((65536+b)>>8))/65536;
        b=(int32_t)((uint32_t)b+(uint32_t)z);
    } while(z>0);
    vector->x=(int32_t)(ox<0?0u-u:u);
    vector->y=(int32_t)(oy<0?0u-v:v);
    uint32_t dot=u*x+v*y;
    length=65536u+(uint32_t)(((int32_t)dot)/65536);
    if(shift>0) length=(length+(1u<<((uint32_t)shift-1u)))>>(uint32_t)shift;
    else length<<=(uint32_t)(-shift);
    return length;
}
