#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <sys/mman.h>
#include <unistd.h>
#include "am_util_stdio.h"
static uint32_t wrapped(char *buf,uint32_t n,const char *fmt,...){va_list ap;va_start(ap,fmt);uint32_t r=am_util_stdio_vsnprintf(buf,n,fmt,ap);va_end(ap);return r;}
int main(int argc,char **argv){
 if(argc!=4)return 90;
 unsigned id=(unsigned)strtoul(argv[1],0,10);uint32_t n=(uint32_t)strtoul(argv[2],0,10);unsigned mode=(unsigned)strtoul(argv[3],0,10);
 size_t page=(size_t)sysconf(_SC_PAGESIZE);unsigned char *m=mmap(0,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0);if(m==MAP_FAILED)return 91;if(mprotect(m+page,page,PROT_READ|PROT_WRITE))return 92;
 memset(m+page,0xa7,page);size_t capacity=n<1024?n:0;unsigned char *out=m+2*page-capacity;uint32_t r;const char *expected="";
 #define CALL(fmt,...) (mode?wrapped((char*)out,n,fmt,##__VA_ARGS__):am_util_stdio_snprintf((char*)out,n,fmt,##__VA_ARGS__))
 switch(id){
 case 0:expected="ABCD";r=CALL("ABCD");break;
 case 1:expected="Q:hi:0007:ab:AB:-12:3:%";r=CALL("%c:%s:%04u:%x:%X:%d:%i:%%",'Q',"hi",7u,0xabu,0xabu,-12,3);break;
 case 2:expected="4294967295";r=CALL("%u",UINT32_MAX);break;
 case 3:expected="    7";r=CALL("%5u",7u);break;
 case 4:expected="1.25";r=CALL("%.2f",1.25);break;
 case 5:expected="";r=CALL("");break;
 case 6:expected="Z";r=CALL("%s","Z");break;
 case 7:expected="-1.25";r=CALL("%.2f",-1.25);break;
 case 8:expected="%q";r=CALL("%%q");break;
 case 9:{char big[1025];memset(big,'x',1024);big[1024]=0;r=CALL("%s",big);expected="";break;}
 case 10:{char big[2050];memset(big,'x',2049);big[2049]=0;r=CALL("%s",big);expected="";break;}
 case 11:expected="";r=CALL((const char *)(m+2*page));break;
 default:return 93;
 }
 size_t len=strlen(expected);int copy=n<1024 && len<n;uint32_t want=copy?(uint32_t)len:0;int good=r==want;
 if(copy)good=good&&!memcmp(out,expected,len);
 for(size_t i=0;i<page;i++){unsigned char want_byte=0xa7;if(copy && i>=page-capacity && i<page-capacity+len)want_byte=(unsigned char)expected[i-(page-capacity)];if(m[page+i]!=want_byte)good=0;}
 printf("{\"id\":%u,\"n\":%u,\"mode\":%u,\"return\":%u,\"expected_return\":%u,\"expected_bytes\":\"%s\",\"full_destination_page_matches\":%s,\"termination_byte_unchanged\":%s}\n",id,n,mode,r,want,expected,good?"true":"false",copy&&capacity>len&&out[len]==0xa7?"true":"false");
 munmap(m,page*3);return good?0:1;
}
