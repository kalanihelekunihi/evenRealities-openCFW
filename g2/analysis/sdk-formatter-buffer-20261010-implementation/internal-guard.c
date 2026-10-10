#include <stdlib.h>
#include <string.h>
#include <sanitizer/asan_interface.h>
/* Include the unchanged vendor file to expose its private buffer to this test-only guard. */
#include "am_util_stdio.c"
int main(int argc,char **argv){
 if(argc!=2)return 90;
 size_t len=(size_t)strtoul(argv[1],0,10);if(len>2049)return 91;
 char input[2050],out[1]={0x55};memset(input,'x',len);input[len]=0;
 /* Explicit shadow guard; no SDK code or buffer declaration is changed. */
 __asan_poison_memory_region(g_prfbuf+sizeof(g_prfbuf),64);
 uint32_t r=am_util_stdio_snprintf(out,1,"%s",input);
 __asan_unpoison_memory_region(g_prfbuf+sizeof(g_prfbuf),64);
 return r==0 && out[0]==0x55 ? 0 : 1;
}
