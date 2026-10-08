/* Locked f89a4c46 boundaries: writer415672, snprintf41b218, vsnprintf41b25c.
 * Independent reconstruction; formatter41e47a remains an explicit dependency. */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
_Static_assert(sizeof(va_list)==4,"ARM cursor ABI required");
static uint32_t cursor_of_va(va_list ap){uint32_t cursor;__builtin_memcpy(&cursor,&ap,4);return cursor;}
typedef struct { uint32_t next,remaining,total; } opencfw_format_sink;
typedef opencfw_format_sink *(*opencfw_format_put)(opencfw_format_sink *,uint32_t);
extern int32_t opencfw_boot_format_engine(opencfw_format_put,opencfw_format_sink *,const char *,uint32_t *,uint32_t);
opencfw_format_sink *opencfw_boot_bounded_writer(opencfw_format_sink *s,uint32_t c){
 s->total++;
 if(s->remaining){uint32_t next=s->next;s->next=next+1;*(volatile uint8_t *)(uintptr_t)next=(uint8_t)c;s->remaining--;}
 return s;
}
static int bounded(char *dst,size_t n,const char *fmt,uint32_t cursor){
 opencfw_format_sink s={(uint32_t)(uintptr_t)(n?dst:0),n?(uint32_t)n-1:0,0};
 int32_t r=opencfw_boot_format_engine(opencfw_boot_bounded_writer,&s,fmt,&cursor,0);
 if(s.next)*(volatile uint8_t *)(uintptr_t)s.next=0;
 return r<0?r:(int32_t)s.total;
}
int opencfw_boot_elog_vsnprintf(char *dst,size_t n,const char *fmt,va_list ap){return bounded(dst,n,fmt,cursor_of_va(ap));}
int opencfw_boot_elog_snprintf(char *dst,size_t n,const char *fmt,...){va_list ap;va_start(ap,fmt);int r=bounded(dst,n,fmt,cursor_of_va(ap));va_end(ap);return r;}
