/* Diagnostic shim only. GNU Arm libm's implementation is not stock source. */
extern double __ieee754_asin(double);
double g2_audio_newlib_asin_probe(double value) {
    return __ieee754_asin(value);
}
