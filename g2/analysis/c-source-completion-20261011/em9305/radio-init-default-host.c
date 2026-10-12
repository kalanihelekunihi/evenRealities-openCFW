#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){if(p!=(void*)0x805b84||n!=112||v)abort();return memset(p,v,n);}
static void *opencfw_em9305_memcpy(void*p,const void*q,uint32_t n){if(p!=(void*)0x805b88||n!=24||*(uint8_t*)0x805bf0!=127)abort();return memcpy(p,q,n);}
#include "radio-init-default-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();uint8_t ex[112]={0};ex[5]=0x88;ex[6]=0x13;ex[9]=0x88;ex[10]=0x13;ex[24]=7;ex[108]=127;for(unsigned v=0;v<256;v++){memset((void*)0x805b84,v,112);if(opencfw_em9305_init_lower_30e9e0(v)!=0x805b88||memcmp((void*)0x805b84,ex,112))abort();}puts("PASS 256 init default sparse-state projections; no native/hardware claim");return 0;}
