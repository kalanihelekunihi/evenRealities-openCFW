/* Independent reconstruction of stock 41e4b6..41e5fa parser fragment.
 * This is a helper for a future engine, not a replacement for its full body. */
#include "format_parser.h"
static int digit(unsigned c){return c>='0'&&c<='9';}
static uint32_t flag(unsigned c){switch(c){case ' ':return 1;case '+':return 2;case '-':return 4;case '#':return 8;case '0':return 16;default:return 0;}}
const char *opencfw_format_parse(const char *percent,uint32_t **cursor,opencfw_format_spec *out){
 const unsigned char *p=(const unsigned char *)percent+1;uint32_t flags=0,bit;int32_t width=0,precision=-1;unsigned length=0;
 while((bit=flag(*p))){flags|=bit;p++;}
 if(*p=='*'){width=(int32_t)*(*cursor)++;p++;if(width<0){width=(int32_t)(0u-(uint32_t)width);flags|=4;}}
 else{while(digit(*p)){if(width<214748363)width=(int32_t)((uint32_t)width*10+*p-'0');p++;}}
 if(*p=='.'){p++;if(*p=='*'){precision=(int32_t)*(*cursor)++;p++;}
 else{int minus=*p=='-';if(minus)p++;precision=0;while(digit(*p)){if(!minus&&precision<214748363)precision=(int32_t)((uint32_t)precision*10+*p-'0');p++;}}}
 switch(*p){case 0:length=*p++;break;case 'h':case 'j':case 'l':case 't':case 'z':case 'L':length=*p++;break;default:break;}
 if(length=='h'&&*p=='h'){length='b';p++;}else if(length=='l'&&*p=='l'){length='q';p++;}
 out->flags=flags;out->width=width;out->precision=precision;out->length=length;out->conversion=*p;return (const char *)p;
}
