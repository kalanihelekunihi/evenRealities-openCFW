#include <stdint.h>
extern uint32_t r1_binary32_classify_bits(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_native_errno_set(uint32_t);
extern float r1_math_low_square32(void);
extern float r1_math_add32(float,float);
__attribute__((section(".r1.math.atan2f_data"),used))
const uint32_t r1_atan2f_data[22]={0xbfc90fdb,0x3fc90fdb,0x40490fdb,0xc0490fdb,0xbfc90000,0xb9fdaa22,0x3fc90000,0x39fdaa22,0x3eed6000,0x37ce0ac3,0,0xc0490000,0xba7daa22,0x40490000,0x3a7daa22,0xbd65ad2d,0x3dd5b88f,0xbe11b50f,0x3e4cc861,0xbeaaaaa8,0x4f800000,0x2f800000};
typedef union {uint32_t bits;float value;} word_float;
static float fbits(uint32_t bits) {word_float x={.bits=bits};return x.value;}
static uint32_t bits(float value) {word_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b) {float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
BINARY(divide,"vdiv.f32")
static float madd(float accumulator,float a,float b)
{__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float msub(float accumulator,float a,float b)
{__asm__ volatile("vmls.f32 %0,%1,%2":"+t"(accumulator):"t"(a),"t"(b));return accumulator;}
static float negate(float value)
{__asm__ volatile("vneg.f32 %0,%0":"+t"(value));return value;}
static uint32_t classify(float value)
{return r1_binary32_classify_bits(bits(value),0,0,0);}
float r1_native_atan2f(float y,float x)
{
    uint32_t ybits=bits(y),xbits=bits(x);
    if ((ybits<<1)+0xe8000000u>=0xe5000000u || (xbits<<1)+0xe8000000u>=0xe5000000u) {
        if ((ybits<<1)>0xff000000u || (xbits<<1)>0xff000000u) return r1_math_add32(y,x);
        if (!((ybits|xbits)<<1)) {xbits|=0x7f800000u;x=fbits(xbits);}
        else if ((ybits<<1)==0xff000000u && (xbits<<1)==0xff000000u) {
            ybits&=~0x40000000u;xbits&=~0x40000000u;y=fbits(ybits);x=fbits(xbits);
        } else if ((ybits<<1)==0xff000000u || !(xbits<<1)) {
            /* Native changes only integer classification words on this path. */
            ybits|=0x7f800000u;xbits&=0x80000000u;
        } else if ((xbits<<1)==0xff000000u || !(ybits<<1)) {
            ybits&=0x80000000u;xbits|=0x7f800000u;
        } else if (!(((xbits<<1)^(ybits<<1))&0x80000000u)) {
            float scale=fbits(r1_atan2f_data[(int32_t)(xbits<<1)>=0 ? 20 : 21]);
            y=mul(y,scale);x=mul(x,scale);ybits=bits(y);xbits=bits(x);
        }
    }
    int32_t difference=(int32_t)((ybits>>23)&255u)-(int32_t)((xbits>>23)&255u);
    if (difference>27) return fbits(r1_atan2f_data[ybits>>31 ? 0 : 1]);
    if (difference< -26) {
        if (xbits>>31) return fbits(r1_atan2f_data[ybits>>31 ? 3 : 2]);
        float ratio=divide(y,x);
        if (classify(ratio)==4) (void)r1_math_low_square32();
        uint32_t yc=classify(y),xc=classify(x),rc=classify(ratio);
        if ((yc==4 || yc==5) && (xc==4 || xc==5) && rc==0) r1_native_errno_set(2);
        return ratio;
    }
    float high,low;
    if ((ybits<<1)>(xbits<<1)) {
        high=fbits(r1_atan2f_data[ybits>>31 ? 4 : 6]);low=fbits(r1_atan2f_data[ybits>>31 ? 5 : 7]);
        float old_x=x;x=negate(y);y=old_x;
        uint32_t old_xbits=xbits;xbits=ybits^0x80000000u;ybits=old_xbits;
    } else if (!(xbits>>31)) high=low=fbits(r1_atan2f_data[10]);
    else {
        high=fbits(r1_atan2f_data[ybits>>31 ? 11 : 13]);low=fbits(r1_atan2f_data[ybits>>31 ? 12 : 14]);
    }
    float ratio;
    if (((xbits-ybits)<<1)<0x1000000u) {
        float half;
        if ((xbits^ybits)>>31) {
            half=fbits(0xbf000000u);high=sub(high,fbits(r1_atan2f_data[8]));low=sub(low,fbits(r1_atan2f_data[9]));
        } else {
            half=fbits(0x3f000000u);high=add(high,fbits(r1_atan2f_data[8]));low=add(low,fbits(r1_atan2f_data[9]));
        }
        float numerator=msub(y,half,x);float denominator=madd(x,y,half);ratio=divide(numerator,denominator);
    } else ratio=divide(y,x);
    float square=mul(ratio,ratio);
    float polynomial=madd(fbits(r1_atan2f_data[16]),square,fbits(r1_atan2f_data[15]));
    polynomial=madd(fbits(r1_atan2f_data[17]),square,polynomial);
    polynomial=madd(fbits(r1_atan2f_data[18]),square,polynomial);
    polynomial=madd(fbits(r1_atan2f_data[19]),square,polynomial);
    float cube=mul(ratio,square),result=madd(low,cube,polynomial);
    result=add(result,ratio);return add(result,high);
}
