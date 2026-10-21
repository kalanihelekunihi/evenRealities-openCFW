/* Experimental C reduction of Main IAR formatter 0x481836.
 * Floating decimal generation is an explicit 0x4d4150..0x4d43a8 lower. */
#include <stdint.h>
#include <stddef.h>
#include "format_part.h"

typedef void *(*g2_put_fn)(void *,uint32_t);
extern int32_t g2_iar_main_float_format(g2_format_part *,uint32_t,uint32_t,
                                         uint32_t,int32_t,int32_t,uint8_t,
                                         uint32_t **);

static int32_t emit(g2_put_fn put,void **context,int32_t *count,uint8_t ch) {
    void *next=put(*context,ch);
    if(!next)return -1;
    *context=next;(*count)++;
    return 0;
}
static int32_t repeat(g2_put_fn put,void **context,int32_t *count,
                      uint8_t ch,int32_t n) {
    for(;n>0;n--)if(emit(put,context,count,ch))return -1;
    return 0;
}
static int32_t bytes(g2_put_fn put,void **context,int32_t *count,
                     const uint8_t *p,uint32_t n) {
    for(uint32_t i=0;i<n;i++)if(emit(put,context,count,p[i]))return -1;
    return 0;
}
static uint32_t number(uint8_t *out,uint32_t low,uint32_t high,
                       uint32_t base,uint32_t upper) {
    uint8_t reverse[65];uint32_t n=0;
    do {
        uint32_t rem=0;
        for(uint32_t bit=64;bit;bit--) {
            uint32_t at=bit-1u;
            rem=(rem<<1u)|(at>=32u?((high>>(at-32u))&1u):((low>>at)&1u));
            if(rem>=base){rem-=base;if(at>=32u)high|=1u<<(at-32u);else low|=1u<<at;}
            else {if(at>=32u)high&=~(1u<<(at-32u));else low&=~(1u<<at);}
        }
        reverse[n++]=(uint8_t)(rem<10u?'0'+rem:(upper?'A':'a')+rem-10u);
    }while(low||high);
    for(uint32_t i=0;i<n;i++)out[i]=reverse[n-1u-i];
    return n;
}
static uint32_t argument(uint32_t **cursor) {return *(*cursor)++;}
static void wide_argument(uint32_t **cursor,uint32_t *low,uint32_t *high) {
    uintptr_t aligned=((uintptr_t)*cursor+7u)&~(uintptr_t)7u;
    *cursor=(uint32_t *)aligned;
    *low=argument(cursor);*high=argument(cursor);
}

int32_t g2_iar_general_format(g2_put_fn put,void *context,const char *format,
                              uint32_t **cursor,uint32_t mode) {
    int32_t written=0;
    while(*format) {
        if(*format!='%') {if(emit(put,&context,&written,(uint8_t)*format++))return -1;continue;}
        const char *p=format+1;
        uint32_t flags=0;
        for(;;) {
            uint32_t bit=0;
            if(*p==' ')bit=1u;else if(*p=='+')bit=2u;else if(*p=='-')bit=4u;
            else if(*p=='#')bit=8u;else if(*p=='0')bit=16u;
            if(!bit)break;
            flags|=bit;p++;
        }
        int32_t width=0,precision=-1;
        if(*p=='*') {width=(int32_t)argument(cursor);p++;if(width<0){width=-width;flags|=4u;}}
        else while((unsigned)(*p-'0')<10u) {if(width<214748364)width=width*10+(*p-'0');p++;}
        if(*p=='.') {
            p++;precision=0;
            if(*p=='*'){precision=(int32_t)argument(cursor);p++;}
            else {
                if(*p=='-') {p++;while((unsigned)(*p-'0')<10u)p++;}
                else while((unsigned)(*p-'0')<10u){if(precision<214748364)precision=precision*10+(*p-'0');p++;}
            }
        }
        uint8_t length=0;
        if(*p=='h'||*p=='j'||*p=='l'||*p=='t'||*p=='z'||*p=='L'){
            length=(uint8_t)*p++;
            if(length=='h'&&*p=='h'){length='b';p++;}
            else if(length=='l'&&*p=='l'){length='q';p++;}
        }
        uint8_t conv=(uint8_t)*p;
        format=p+(*p!=0);
        g2_format_part part={0};
        if(conv=='n') {
            if(mode)return -1;
            uintptr_t target=argument(cursor);
            if(!target)return -1;
            if(length=='b')*(uint8_t *)target=(uint8_t)written;
            else if(length=='h')*(uint16_t *)target=(uint16_t)written;
            else if(length=='j'||length=='q') {((uint32_t *)target)[0]=(uint32_t)written;((uint32_t *)target)[1]=(uint32_t)(written>>31);}
            else *(uint32_t *)target=(uint32_t)written;
            continue;
        }
        if(conv=='%'){part.prefix[0]='%';part.prefix_len=1;}
        else if(conv=='c'){part.prefix[0]=(uint8_t)argument(cursor);part.prefix_len=1;}
        else if(conv=='s'){
            const uint8_t *str=(const uint8_t *)(uintptr_t)argument(cursor);
            if(!str){if(mode)return -1;str=(const uint8_t *)"";}
            uint32_t n=0;
            while(str[n]&&(precision<0||n<(uint32_t)precision))n++;
            part.body_len=n;
            /* Direct string emission below avoids a fixed-size copy. */
            int32_t pad=width-(int32_t)n;
            if(!(flags&4u)&&repeat(put,&context,&written,' ',pad))return -1;
            if(bytes(put,&context,&written,str,n))return -1;
            if((flags&4u)&&repeat(put,&context,&written,' ',pad))return -1;
            continue;
        }
        else if(conv=='d'||conv=='i'||conv=='u'||conv=='o'||conv=='x'||conv=='X'||conv=='p'){
            uint32_t low,high=0;uint32_t sign=(conv=='d'||conv=='i');
            if(length=='j'||length=='q')wide_argument(cursor,&low,&high);
            else {
                low=argument(cursor);
                if(length=='b')low=sign?(uint32_t)(int32_t)(int8_t)low:(low&0xffu);
                else if(length=='h')low=sign?(uint32_t)(int32_t)(int16_t)low:(low&0xffffu);
                high=sign&&((int32_t)low<0)?UINT32_MAX:0u;
            }
            if(sign&&((int32_t)high<0)) {
                part.prefix[part.prefix_len++]='-';
                low=~low+1u;high=~high+(low==0u);
            } else if(sign&&(flags&2u))part.prefix[part.prefix_len++]='+';
            else if(sign&&(flags&1u))part.prefix[part.prefix_len++]=' ';
            uint32_t base=(conv=='o')?8u:((conv=='x'||conv=='X'||conv=='p')?16u:10u);
            if((flags&8u)&&(conv=='x'||conv=='X')&&(low||high)) {
                part.prefix[part.prefix_len++]='0';part.prefix[part.prefix_len++]=conv;
            }
            part.body_len=number(part.body,low,high,base,conv=='X');
            if(precision==0&&low==0u&&high==0u)part.body_len=0;
            if(precision>(int32_t)part.body_len)part.lead_zero=(uint32_t)(precision-(int32_t)part.body_len);
            if((flags&16u)&&!(flags&4u)&&precision<0) {
                int32_t zeros=width-(int32_t)(part.prefix_len+part.body_len+part.mid_zero);
                if(zeros>0)part.lead_zero=(uint32_t)zeros;
            }
        }
        else if(conv=='a'||conv=='A'||conv=='e'||conv=='E'||conv=='f'||conv=='F'||conv=='g'||conv=='G') {
            int32_t err=g2_iar_main_float_format(&part,flags,(uint32_t)width,
                                                  (uint32_t)precision,precision,width,conv,cursor);
            if(err)return err;
        }
        else {part.prefix[0]='%';part.prefix_len=1;if(conv)part.prefix[part.prefix_len++]=conv;}
        int32_t pad=width-(int32_t)(part.prefix_len+part.body_len+part.suffix_len+
                                   part.lead_zero+part.mid_zero+part.trail_zero);
        if(!(flags&4u)&&repeat(put,&context,&written,' ',pad))return -1;
        if(bytes(put,&context,&written,part.prefix,part.prefix_len))return -1;
        if(repeat(put,&context,&written,'0',(int32_t)part.lead_zero))return -1;
        if(bytes(put,&context,&written,part.body,part.body_len))return -1;
        if(repeat(put,&context,&written,'0',(int32_t)part.mid_zero))return -1;
        if(bytes(put,&context,&written,part.suffix,part.suffix_len))return -1;
        if(repeat(put,&context,&written,'0',(int32_t)part.trail_zero))return -1;
        if((flags&4u)&&repeat(put,&context,&written,' ',pad))return -1;
    }
    return written;
}
