/* GH3X2X demo-code logging hook. Keep its varargs intact for the R1
 * source-owned formatter and synchronous RTT writer. */
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

extern int r1_native_vsnprintf(char *,size_t,const char *,va_list);
extern uint32_t r1_stdout_write(uint32_t,volatile void *,uint32_t);

void gh3x2x_print_fmt(const char *format,...)
{
    if(format==NULL)return;
    char message[256];
    va_list arguments;
    va_start(arguments,format);
    int count=r1_native_vsnprintf(message,sizeof(message),format,arguments);
    va_end(arguments);
    if(count<=0)return;
    uint32_t length=(uint32_t)count;
    if(length>=sizeof(message))length=sizeof(message)-1u;
    (void)r1_stdout_write(0,message,length);
}
