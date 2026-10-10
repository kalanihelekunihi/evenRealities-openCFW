/* Analysis interface only; not a linked production implementation. */
#ifndef OPENCFW_ANALYSIS_LZ4_STOCK_CONTRACT_H
#define OPENCFW_ANALYSIS_LZ4_STOCK_CONTRACT_H
#include <stdint.h>
#define OPENCFW_STOCK_LZ4_SAFE_ADDR UINT32_C(0x0054f338)
#define OPENCFW_STOCK_LZ4_CALLER_ADDR UINT32_C(0x004e0c0c)
/* safe: positive output length, zero empty success, negative consumed-position error */
typedef int32_t (*opencfw_stock_lz4_safe_fn)(const void*,void*,int32_t,int32_t);
/* caller: argument order differs; returns positive length or zero */
typedef int32_t (*opencfw_stock_lz4_caller_fn)(const void*,int32_t,void*,int32_t);
#endif
