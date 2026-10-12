#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
extern uint32_t gx8002_image_b_format_emit_10008a04(uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t),uint32_t,uint32_t,uint32_t,const uint8_t*,uint32_t,uint32_t,uint32_t);
static char out[64];static uint32_t count,begin;
static uint32_t emit(uint32_t c,uint32_t ctx,uint32_t index,uint32_t state){assert(ctx==21&&state==32&&index==begin+count);out[count++]=(char)c;return 0;}
static void run(const char *expected,const char *reverse,uint32_t n,uint32_t width,uint32_t flags){memset(out,0,sizeof out);count=0;begin=7;uint32_t end=gx8002_image_b_format_emit_10008a04(emit,21,begin,32,(const uint8_t*)reverse,n,width,flags);assert(end==begin+count);assert(strcmp(out,expected)==0);}
int main(void){run("   ba","ab",2,5,0);run("ba   ","ab",2,5,2);run("ba","ab",2,5,1);run("   ","",0,3,0);run("   ","",0,3,2);run("ba","ab",2,1,0);puts("6/6 formatter emit branch fixtures");return 0;}
