/* SPDX-License-Identifier: MIT
 * Functional freestanding support for source littlefs. These are standard-C
 * behavior implementations, not asserted exact stock IAR runtime bodies. */
#include <stddef.h>
#include <stdint.h>
void *memcpy(void *out,const void *in,size_t size) {uint8_t *d=out;const uint8_t *s=in;for(size_t i=0;i<size;i++)d[i]=s[i];return out;}
void *memset(void *out,int value,size_t size) {uint8_t *d=out;for(size_t i=0;i<size;i++)d[i]=(uint8_t)value;return out;}
int memcmp(const void *left,const void *right,size_t size) {const uint8_t *a=left,*b=right;for(size_t i=0;i<size;i++)if(a[i]!=b[i])return (int)a[i]-(int)b[i];return 0;}
size_t strlen(const char *text) {size_t i=0;while(text[i])i++;return i;}
char *strcpy(char *out,const char *in) {size_t i=0;do {out[i]=in[i];}while(in[i++]);return out;}
char *strchr(const char *text,int character) {uint8_t c=(uint8_t)character;do {if((uint8_t)*text==c)return (char *)text;}while(*text++);return 0;}
size_t strspn(const char *text,const char *set) {size_t i=0;for(;text[i];i++)if(!strchr(set,text[i]))break;return i;}
size_t strcspn(const char *text,const char *set) {size_t i=0;for(;text[i];i++)if(strchr(set,text[i]))break;return i;}
