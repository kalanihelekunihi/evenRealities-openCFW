/* math.h for building google/liblc3 v1.1.3 (96a3af0b) as linked in G2
 * 2.2.6.10 (IAR, Cortex-M55, VFP calling convention).
 *
 * The reconstruction profile is freestanding (-ffreestanding -fno-builtin),
 * so libm calls stay calls unless mapped to a builtin here. Evidence from the
 * stock encoder code (0x438400..0x439b78, 0x590dc8..0x5915a2,
 * 0x598284..0x59c7ac):
 *   - fabsf is inlined (vabs.f32 at 0x59b290, 0x59b7c8, 0x59c290, ...);
 *   - sqrtf is an out-of-line IAR libm call, bl 0x4397a8 (6 sites: ltpf
 *     0x4392c6/0x439302/0x439576, mdct 0x598db6, sns 0x59a68a, spec
 *     0x59bd44); 0x4397a8 is vcmpe/vsqrt with an EDOM tail call 0x439ca4;
 *   - fmaxf bl 0x439f88 (9 sites), fminf bl 0x439efc (1), floorf
 *     bl 0x43a5a0 (1), roundf bl 0x577d08 (1), truncf bl 0x59f510 (1).
 *   - log10f has no call site: its only use, log10f(2) in fastmath.h
 *     lc3_log10f, is a compile-time constant (folded by IAR).
 * All of these take and return floats in s0/s1 (hard-float ABI).
 * Confidence: Proven (call/inline split), Compat (this header itself). */
#ifndef G2_LIBLC3_MATH_H
#define G2_LIBLC3_MATH_H

float sqrtf(float);
float fmaxf(float, float);
float fminf(float, float);
float floorf(float);
float roundf(float);
float truncf(float);

#define fabsf(x) __builtin_fabsf(x)
#define log10f(x) __builtin_log10f(x)

#endif /* G2_LIBLC3_MATH_H */
