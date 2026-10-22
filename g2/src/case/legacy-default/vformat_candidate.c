/* SPDX-License-Identifier: MIT
 * CASE formatter source candidate for native 0x08009210. ARM word-stream interface is taken from
 * the retained logger wrapper. Conversion details require stock comparison.
 */
#include <stdint.h>
#include <stddef.h>

typedef int32_t (*case_emit_t)(int32_t, void *);
enum { LEFT=1, PLUS=2, SPACE=4, ZERO=8, ALT=16, PTR=32 };
enum { DEF, HH, H, L, LL, J, Z, T, BIGL };

static uint32_t next_word(const uint32_t **words) { return *(*words)++; }
static uint64_t next_wide(const uint32_t **words)
{
    uintptr_t p=(uintptr_t)*words;
    p=(p+7u)&~(uintptr_t)7u;
    const uint32_t *aligned=(const uint32_t *)p;
    uint64_t value=(uint64_t)aligned[0]|((uint64_t)aligned[1]<<32);
    *words=aligned+2;
    return value;
}
static void output(case_emit_t emit,void *context,uint32_t *count,char c)
{
    (void)emit((unsigned char)c,context);
    ++*count;
}
static void repeat(case_emit_t emit,void *context,uint32_t *count,char c,
                   uint32_t n)
{
    while(n--) output(emit,context,count,c);
}
static uint32_t parse_number(const char **format)
{
    uint32_t n=0;
    while(**format>='0'&&**format<='9') {
        uint32_t d=(uint32_t)(*(*format)++-'0');
        n=(n>429496729u || (n==429496729u && d>5u))
            ? UINT32_MAX : n*10u+d;
    }
    return n;
}
static uint64_t get_unsigned(const uint32_t **args,int length)
{
    uint64_t v=(length==LL||length==J)?next_wide(args):next_word(args);
    if(length==HH) return (uint8_t)v;
    if(length==H) return (uint16_t)v;
    return v;
}
static int64_t get_signed(const uint32_t **args,int length)
{
    uint64_t v=get_unsigned(args,length);
    if(length==HH) return (int8_t)v;
    if(length==H) return (int16_t)v;
    if(length==LL||length==J) return (int64_t)v;
    return (int32_t)v;
}
/* Source-owned radix division; only bases 8, 10 and 16 reach this helper.
 * The 32-bit limbs avoid an opaque ARM compiler runtime arithmetic import. */
static uint32_t divide_radix(uint64_t *number,uint32_t radix)
{
    uint32_t hi=(uint32_t)(*number>>32),lo=(uint32_t)*number;
    uint32_t quotient_hi=0,quotient_lo=0,remainder=0;
    for(int bit=63;bit>=0;--bit) {
        uint32_t digit=bit>=32 ? ((hi>>(bit-32))&1u) : ((lo>>bit)&1u);
        remainder=(remainder<<1)|digit;
        if(remainder>=radix) {
            remainder-=radix;
            if(bit>=32) quotient_hi|=1u<<(bit-32);
            else quotient_lo|=1u<<bit;
        }
    }
    *number=((uint64_t)quotient_hi<<32)|quotient_lo;
    return remainder;
}
static void put_number(case_emit_t emit,void *context,uint32_t *count,
                       uint64_t value,int negative,unsigned base,int upper,
                       unsigned flags,uint32_t width,int32_t precision)
{
    const int nonzero=value!=0u;
    char reverse[65];
    uint32_t digits=0;
    static const char low[]="0123456789abcdef";
    static const char high[]="0123456789ABCDEF";
    const char *alphabet=upper?high:low;
    if(value==0) {
        if(precision!=0) reverse[digits++]='0';
    } else {
        while(value) {reverse[digits++]=alphabet[divide_radix(&value,base)];}
    }
    char sign=negative?'-':(flags&PLUS)?'+':(flags&SPACE)?' ':0;
    char prefix1=0,prefix2=0;
    if(flags&ALT) {
        if(flags&PTR) prefix1='@';
        else if(base==16 && nonzero) {prefix1='0';prefix2=upper?'X':'x';}
        else if(base==8 && (!digits||
                (precision<=(int32_t)digits && reverse[digits-1]!='0'))) prefix1='0';
    }
    uint32_t zeros=precision>(int32_t)digits?(uint32_t)precision-digits:0;
    uint32_t used=digits+zeros+(sign!=0)+(prefix1!=0)+(prefix2!=0);
    uint32_t pad=width>used?width-used:0;
    char padchar=(flags&ZERO)&&!(flags&LEFT)&&precision<0?'0':' ';
    if(!(flags&LEFT)&&padchar==' ') repeat(emit,context,count,' ',pad);
    if(sign) output(emit,context,count,sign);
    if(prefix1) output(emit,context,count,prefix1);
    if(prefix2) output(emit,context,count,prefix2);
    if(!(flags&LEFT)&&padchar=='0') repeat(emit,context,count,'0',pad);
    repeat(emit,context,count,'0',zeros);
    while(digits) output(emit,context,count,reverse[--digits]);
    if(flags&LEFT) repeat(emit,context,count,' ',pad);
}

/* Stock 0x08009210 (case_vformat) */
int32_t case_vformat(const char *format,const uint32_t *arguments,
                     void *context,case_emit_t emit)
{
    const uint32_t *args=arguments;
    uint32_t count=0;
    while(*format) {
        if(*format!='%') {output(emit,context,&count,*format++);continue;}
        ++format;
        unsigned flags=0;
        for(;;) {
            if(*format=='-') flags|=LEFT;
            else if(*format=='+') flags|=PLUS;
            else if(*format==' ') flags|=SPACE;
            else if(*format=='0') flags|=ZERO;
            else if(*format=='#') flags|=ALT;
            else break;
            ++format;
        }
        uint32_t width=0;
        if(*format=='*') {
            int32_t w=(int32_t)next_word(&args);++format;
            if(w<0) {flags|=LEFT;width=(uint32_t)(-(int64_t)w);}
            else width=(uint32_t)w;
        } else width=parse_number(&format);
        int32_t precision=-1;
        if(*format=='.') {
            ++format;
            if(*format=='*') {precision=(int32_t)next_word(&args);++format;}
            else precision=(int32_t)parse_number(&format);
            if(precision<0) precision=-1;
        }
        int length=DEF;
        if(*format=='h') {++format;length=*format=='h'?(++format,HH):H;}
        else if(*format=='l') {++format;length=*format=='l'?(++format,LL):L;}
        else if(*format=='j') {++format;length=J;}
        else if(*format=='z') {++format;length=Z;}
        else if(*format=='t') {++format;length=T;}
        else if(*format=='L') {++format;length=BIGL;}
        char conversion=*format;
        if(!conversion) break;
        ++format;
        if(conversion=='d'||conversion=='i') {
            int64_t signed_value=get_signed(&args,length);
            int negative=signed_value<0;
            uint64_t magnitude=negative?(uint64_t)(-(signed_value+1))+1u:(uint64_t)signed_value;
            put_number(emit,context,&count,magnitude,negative,10,0,flags,width,precision);
        } else if(conversion=='u'||conversion=='o'||conversion=='x'||conversion=='X'||conversion=='p') {
            uint64_t value=get_unsigned(&args,length);
            unsigned base=conversion=='o'?8u:conversion=='u'?10u:16u;
            if(conversion=='p' && precision<8) precision=8;
            put_number(emit,context,&count,value,0,base,conversion=='X',
                       (flags&~(PLUS|SPACE))|(conversion=='p'?PTR:0u),width,precision);
        } else if(conversion=='c') {
            char c=(char)next_word(&args);
            uint32_t characters=precision==0?0u:1u;
            uint32_t pad=width>characters?width-characters:0;
            char padding=(flags&ZERO)&&!(flags&LEFT)?'0':' ';
            if(!(flags&LEFT)) repeat(emit,context,&count,padding,pad);
            if(characters!=0u)output(emit,context,&count,c);
            if(flags&LEFT) repeat(emit,context,&count,' ',pad);
        } else if(conversion=='s') {
            const char *s=(const char *)(uintptr_t)next_word(&args);
            uint32_t n=0;
            while((precision<0||n<(uint32_t)precision) && s[n]) ++n;
            uint32_t pad=width>n?width-n:0;
            char padding=(flags&ZERO)&&!(flags&LEFT)?'0':' ';
            if(!(flags&LEFT)) repeat(emit,context,&count,padding,pad);
            for(uint32_t i=0;i<n;++i) output(emit,context,&count,s[i]);
            if(flags&LEFT) repeat(emit,context,&count,' ',pad);
        } else if(conversion=='n') {
            void *p=(void *)(uintptr_t)next_word(&args);
            if(length==HH) *(int8_t *)p=(int8_t)count;
            else if(length==H) *(int16_t *)p=(int16_t)count;
            else if(length==LL||length==J) *(int64_t *)p=(int64_t)count;
            else *(int32_t *)p=(int32_t)count;
        } else output(emit,context,&count,conversion);
    }
    return (int32_t)count;
}
