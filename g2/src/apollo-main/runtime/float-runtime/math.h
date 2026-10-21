#ifndef AUDIO_FLOAT_RUNTIME_H
#define AUDIO_FLOAT_RUNTIME_H
/* Reconstructed IEEE-754 binary32 bit algorithms, not host-libc adapters.
 * floor/round/ceil preserve nonfinite input bits without raising FPSCR flags.
 * fmod canonicalizes relevant invalid cases; denominator-zero domain errors
 * write stock errno word. Do not infer standard-libc exception behavior. */
float audio_floorf(float input);
float audio_roundf(float input);
float audio_ceilf(float input);
float audio_fmodf(float numerator, float denominator);
#endif
