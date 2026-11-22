#ifndef G2C_FUEL_GAUGE_LEAVES_H
#define G2C_FUEL_GAUGE_LEAVES_H

#include <stdint.h>
#include <stddef.h>

/* Leaf callees of nrf_model_process / nrf_model_init. See the .c for ABI notes. */
uint64_t fg_43a110(uint32_t bits);
int      fg_43a19c(uint32_t lo0, uint32_t hi0, uint32_t lo1, uint32_t hi1);
int      fg_43a0f4(float x);
float    fg_439efc(float a, float b);
float    fg_439f88(float a, float b);
float    fg_43a5a0(float x);
uint32_t fg_43a5b0(uint32_t bits);
void     nrf_model_tte_params_58eab0(void *state, const float params[2]);

void    *fg_memcpy(void *dst, const void *src, size_t n);
void    *fg_memset(void *dst, int c, size_t n);
void     fg_439ca4(void);
float    fg_4397a8(float x);
float    fg_439e9c(const float a[3]);
float    fg_439f24(const float a[3]);
int      fg_439fb4(const uint8_t *s, int32_t *out);
void     fg_43ba6c(const float *src, const int32_t *count_ptr, float *dst, int32_t out[2]);
void     fg_43bc58(const float *src, const int32_t *p, float *dst, int32_t out[2]);
int      fg_43baf4(uint32_t lo0, uint32_t hi0, uint32_t lo1, uint32_t hi1);

#endif
