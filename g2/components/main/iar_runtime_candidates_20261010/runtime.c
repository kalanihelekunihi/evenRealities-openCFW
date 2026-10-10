#include "runtime.h"
_Static_assert(sizeof(g2_scan_state)==20,"scan layout");
_Static_assert(sizeof(g2_output_state)==48,"output layout");
int32_t g2_isxdigit(int32_t c) { return ((uint32_t)c-48u<10u)||((uint32_t)c-65u<6u)||((uint32_t)c-97u<6u); }
uint8_t *g2_strcat(uint8_t *d,const uint8_t *s) {uint8_t *ret=d;while(*d)++d;while((*d++=*s++)!=0){}return ret;}
uint32_t g2_strcspn(const uint8_t *s,const uint8_t *set) {const uint8_t *p=s;for(;*p;++p){const uint8_t *q=set;while(*q && *q!=*p)++q;if(*q)break;}return (uint32_t)(p-s);}
uint32_t g2_strspn(const uint8_t *s,const uint8_t *set) {const uint8_t *p=s;for(;*p;++p){const uint8_t *q=set;while(*q && *q!=*p)++q;if(!*q)break;}return (uint32_t)(p-s);}
uint8_t *g2_strrchr(const uint8_t *s,int32_t c) {const uint8_t *r=0;do{if(*s==(uint8_t)c)r=s;}while(*s++);return (uint8_t *)r;}
int32_t g2_putchars(g2_output_callback f,g2_output_state *s,const uint8_t *p,uint32_t n) {while(n--){s->context=f(s->context,*p++);if(!s->context)return -1;s->count++;}return 0;}
int32_t g2_getn(g2_scan_callback f,g2_scan_state *s) {s->consumed++;s->width--;if(s->width&0x80000000u)return -1;return f(s->context,0,1);}
void g2_ungetn(g2_scan_callback f,g2_scan_state *s,int32_t c) {s->consumed--;if(c!=-1)(void)f(s->context,c,0);}
int32_t g2_ranmatch(const uint8_t *p,int32_t c,uint32_t n) {uint32_t b=(uint8_t)c;while(n){if(n>=3 && p[1]=='-'){if(b>=p[0] && b<=p[2])return 1;p+=3;n-=3;}else{if(*p++==b)return 1;--n;}}return 0;}
const uint32_t *g2_zero_init3(const uint32_t *p,uint32_t base) {uint32_t n;while((n=*p++)!=0){uint32_t a=*p++;if(a&1)a+=base-1;uint32_t *d=(uint32_t *)(uintptr_t)a;do{n-=4;*d++=0;}while(n>=4);uint8_t *b=(uint8_t *)d;if(n&2){*(uint16_t *)b=0;b+=2;}if(n&1)*b=0;}return p;}
