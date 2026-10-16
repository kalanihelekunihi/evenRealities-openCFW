#include <stdint.h>
typedef uint32_t (*output_fn)(uint32_t,uint32_t);
extern uint32_t r1_format_width_padding(uint32_t,uint32_t,uint32_t,output_fn);
extern uint32_t r1_format_left_padding(uint32_t,uint32_t,uint32_t,output_fn);
extern uint64_t r1_runtime_udivmod(uint64_t,uint64_t,uint64_t *);
extern uint32_t r1_format_decimal_digits(volatile uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
#define DATA(name,section_name,value) __attribute__((section(section_name),used)) const uint8_t name[20]=value
__attribute__((section(".r1.format.flags"),used)) const uint32_t r1_format_flag_mask=0x12809;
DATA(r1_format_lower,".r1.format.lower","0123456789abcdef");
DATA(r1_format_upper,".r1.format.upper","0123456789ABCDEF");
__attribute__((section(".r1.format.minus"),used)) const uint8_t r1_format_minus[4]={'-',0,0,0};
__attribute__((section(".r1.format.plus"),used)) const uint8_t r1_format_plus[4]={'+',0,0,0};
__attribute__((section(".r1.format.space"),used)) const uint8_t r1_format_space[4]={' ',0,0,0};
static uint32_t next32(volatile uint32_t **args)
{ uint32_t x=**args;*args+=1;return x; }
static uint64_t next64(volatile uint32_t **args)
{
    *args=(volatile uint32_t *)(uintptr_t)(((uint32_t)(uintptr_t)*args+7u)&~7u);
    uint32_t low=next32(args),high=next32(args);
    return ((uint64_t)high<<32)|low;
}
static uint32_t flag_bit(uint32_t c)
{ uint32_t n=(c-32u)&255u;return n<32 ? 1u<<n : 0; }
/* Recovered parser: all arithmetic is explicitly wrapped at native widths.
 * Callback return values are ignored. Private C frames are not a claim of
 * original stack/register identity; the original body is 136 stack bytes. */
uint32_t r1_format_core(volatile const uint8_t *format,volatile uint32_t *args,
                        uint32_t context,output_fn output)
{
    uint32_t count=0;
    for (;;) {
        uint32_t code=*format;
        if (!code) return count;
        if (code!='%') { output(code,context);++count;++format;continue; }
        uint32_t flags=0,width=0,precision=0;
        ++format;
        for (;;) {
            uint32_t bit=flag_bit(*format);
            if (!(bit&r1_format_flag_mask)) break;
            flags|=bit;++format;
        }
        if (*format=='*') {
            width=next32(&args);++format;flags|=2;
            if ((int32_t)width<0) { flags|=0x2000;width=0u-width; }
        } else while ((uint32_t)(*format-'0')<10) { flags|=2;width=width*10u+*format-'0';++format; }
        if (*format=='.') {
            flags|=4;++format;
            if (*format=='*') { precision=next32(&args);++format; }
            else while ((uint32_t)(*format-'0')<10) { precision=precision*10u+*format-'0';++format; }
        }
        uint32_t length=*format;
        if (length=='l' || length=='h') {
            flags|=length=='l' ? 0x100000u : 0x300000u;
            ++format;
            if (*format==length) { flags+=0x100000u;++format; }
        } else if (length=='j') { flags|=0x200000u;++format; }
        else if (length=='L' || length=='t' || length=='z') ++format;
        code=*format;length=(flags&0x7fffffu)>>20;
        if (!code) return count;
        if (code=='n') {
            uint32_t address=next32(&args);
            if (length==2) { *(volatile uint32_t *)(uintptr_t)address=count;*(volatile uint32_t *)(uintptr_t)(address+4u)=(uint32_t)((int32_t)count>>31); }
            else if (length==3) *(volatile uint16_t *)(uintptr_t)address=(uint16_t)count;
            else if (length==4) *(volatile uint8_t *)(uintptr_t)address=(uint8_t)count;
            else *(volatile uint32_t *)(uintptr_t)address=count;
        } else if (code=='s' || code=='c') {
            uint8_t single[2];volatile const uint8_t *string;uint32_t size=0;
            if (code=='c') { single[0]=(uint8_t)next32(&args);single[1]=0;string=single; }
            else string=(volatile const uint8_t *)(uintptr_t)next32(&args);
            while (!(flags&4) || (int32_t)size<(int32_t)precision) {
                if (!(code=='c' && size<1u) && !string[size]) break;
                ++size;
            }
            width-=size;
            count+=r1_format_width_padding(width,flags,context,output)+size;
            while (size--) { output(*string,context);++string; }
            count+=r1_format_left_padding(width,flags,context,output);
        } else if (code=='d' || code=='i' || code=='u' || code=='o' || code=='x' || code=='X' || code=='p') {
            uint32_t radix=code=='o' ? 8 : (code=='x' || code=='X' || code=='p') ? 16 : 10;
            if (code=='p') { flags|=4;precision=8; }
            uint64_t value=length==2 ? next64(&args) : next32(&args);
            uint8_t prefix[2];uint32_t prefix_size=0;
            if (code=='d' || code=='i') {
                if (length!=2) {
                    uint32_t word=(uint32_t)value;
                    if (length==3) word=(uint32_t)(int32_t)(int16_t)word;
                    if (length==4) word=(uint32_t)(int32_t)(int8_t)word;
                    value=((uint64_t)(uint32_t)((int32_t)word>>31)<<32)|word;
                }
                if (value>>63) { value=0u-value;prefix[0]='-';prefix_size=1; }
                else if (flags&0x800) { prefix[0]='+';prefix_size=1; }
                else if (flags&1) { prefix[0]=' ';prefix_size=1; }
            } else {
                if (length==3) value&=65535u;
                if (length==4) value&=255u;
                if (flags&8) {
                    if (*format=='p') { prefix[0]='@';prefix_size=1; }
                    else if (radix==16 && value) { prefix[0]='0';prefix[1]=*format;prefix_size=2; }
                    if (radix==8 && (value || (flags&4))) { prefix[0]='0';prefix_size=1;--precision; }
                }
            }
            const uint8_t *alphabet=*format=='X' ? r1_format_upper : r1_format_lower;
            uint8_t digits[32];uint32_t first=32;
            while (value) { uint64_t remainder;value=r1_runtime_udivmod(value,radix,&remainder);digits[--first]=alphabet[(uint32_t)remainder]; }
            uint32_t digit_count=32u-first,zeros=0;
            if (flags&4) flags&=~0x10000u;else precision=1;
            if ((int32_t)digit_count<(int32_t)precision) zeros=precision-digit_count;
            width-=zeros+digit_count+prefix_size;
            if (!(flags&0x10000)) count+=r1_format_width_padding(width,flags,context,output);
            for (uint32_t i=0;i<prefix_size;++i) { output(prefix[i],context);++count; }
            if (flags&0x10000) count+=r1_format_width_padding(width,flags,context,output);
            while ((int32_t)zeros>0) { output('0',context);++count;--zeros; }
            while (first<32) { output(digits[first++],context);++count; }
            count+=r1_format_left_padding(width,flags,context,output);
        } else if (code=='e' || code=='E' || code=='f' || code=='F' || code=='g' || code=='G') {
            if (!(flags&4)) precision=6;
            uint64_t bits=next64(&args);
            volatile const uint8_t *prefix=bits>>63 ? r1_format_minus : (flags&0x800) ? r1_format_plus : (flags&1) ? r1_format_space : r1_format_lower+16;
            uint32_t converted[4];uint8_t storage[32];uint32_t total,start=0,point,exponent=0x80000000u;
            code=*format;
            uint32_t requested,mode;
            if (code=='e' || code=='E') { requested=(int32_t)precision<17 ? precision+1u : 17;mode=0; }
            else if (code=='f' || code=='F') { requested=precision;mode=1; }
            else { if ((int32_t)precision<1) precision=1;requested=(int32_t)precision>17 ? 17 : precision;mode=0; }
            r1_format_decimal_digits(converted,(uint32_t)(uintptr_t)storage,(uint32_t)bits,(uint32_t)(bits>>32)&0x7fffffffu,requested,mode);
            volatile const uint8_t *digits=(volatile const uint8_t *)(uintptr_t)converted[0];uint32_t available=converted[2],decimal_exponent=converted[1];
            if (code=='e' || code=='E') { total=precision+1u;point=1;exponent=decimal_exponent; }
            else if (code=='f' || code=='F') {
                total=available;
                if (!converted[3]) total=decimal_exponent+precision+1u;
                if ((int32_t)(precision-total)>=0) { start=0u-1u-(precision-total);total=precision+1u; }
                point=total-precision;
            } else {
                total=precision;
                if (!(flags&8)) {
                    if ((int32_t)available<(int32_t)precision) total=available;
                    while ((int32_t)total>1 && digits[total-1]=='0') --total;
                }
                if ((int32_t)precision<=(int32_t)decimal_exponent || (int32_t)decimal_exponent< -4) { point=1;exponent=decimal_exponent; }
                else {
                    if ((int32_t)decimal_exponent<1) { total-=decimal_exponent;start=decimal_exponent; }
                    else if ((int32_t)total<(int32_t)(decimal_exponent+1u)) total=decimal_exponent+1u;
                    point=decimal_exponent+1u-start;
                }
            }
            if (!(flags&8) && (int32_t)total<=(int32_t)point) point=0xffffffffu;
            uint8_t suffix[16];uint32_t suffix_first=16;
            if (exponent!=0x80000000u) {
                uint32_t magnitude=(int32_t)exponent<0 ? 0u-exponent : exponent,n=0;
                do { suffix[--suffix_first]=(uint8_t)(magnitude%10u+'0');magnitude/=10u;++n; } while (n<2 || magnitude);
                suffix[--suffix_first]=(int32_t)exponent<0 ? '-' : '+';
                suffix[--suffix_first]=(uint8_t)((*format&0x20u)|'E');
            }
            uint32_t suffix_size=16u-suffix_first,prefix_size=*prefix!=0;
            width-=total+(uint32_t)((int32_t)point>>31)+prefix_size+suffix_size+1u;
            if (!(flags&0x10000)) count+=r1_format_width_padding(width,flags,context,output);
            if (*prefix) { output(*prefix,context);++count; }
            if (flags&0x10000) count+=r1_format_width_padding(width,flags,context,output);
            while ((int32_t)total>0) {
                uint32_t byte=(int32_t)start<0 || (int32_t)available<=(int32_t)start ? '0' : digits[start];
                output(byte,context);++count;++start;--total;--point;
                if (!point) { output('.',context);++count; }
            }
            while (suffix_first<16) { output(suffix[suffix_first++],context);++count; }
            count+=r1_format_left_padding(width,flags,context,output);
        } else { output(code,context);++count; }
        ++format;
    }
}
