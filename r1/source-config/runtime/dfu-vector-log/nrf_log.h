#ifndef R1_DFU_VECTOR_LOG_PORT_H
#define R1_DFU_VECTOR_LOG_PORT_H
#include <stdint.h>
extern void r1_dfu_vector_log_info(const char *,const char *,uint32_t);
extern void r1_dfu_vector_log_error(const char *,const char *);
#define R1_DFU_TEXT_1(x) #x
#define R1_DFU_TEXT(x) R1_DFU_TEXT_1(x)
#define R1_DFU_LITERAL(kind,text) \
 static const char kind[(sizeof(text)+3u)&~3u] \
 __attribute__((section(".r1.dfu.vector." #kind "." R1_DFU_TEXT(__LINE__)),used))=text
/* Recovered dual logging, limited to this upstream vector-table translation unit. */
#define NRF_LOG_INFO(format,value) do { \
 R1_DFU_LITERAL(ring,"[RING]" format);R1_DFU_LITERAL(sdk,format); \
 r1_dfu_vector_log_info(ring,sdk,(value)); \
} while(0)
#define NRF_LOG_ERROR(format) do { \
 R1_DFU_LITERAL(ring,"[RING]" format);R1_DFU_LITERAL(sdk,format); \
 r1_dfu_vector_log_error(ring,sdk); \
} while(0)
#endif
