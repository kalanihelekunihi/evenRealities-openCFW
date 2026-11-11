/* Public hard-float C names needed by the Goodix and quantized sensor
 * consumers. Keep the existing canonical recovered algorithms and errno
 * behavior; these are typed entry adapters, not alternative implementations. */
extern double r1_native_atan(double),r1_native_sqrt(double);
extern float r1_native_sqrtf(float),r1_native_floorf(float);
extern float r1_native_fmaxf(float,float),r1_native_expf(float),r1_native_tanhf(float);
double atan(double value) { return r1_native_atan(value); }
double sqrt(double value) { return r1_native_sqrt(value); }
float sqrtf(float value) { return r1_native_sqrtf(value); }
float floorf(float value) { return r1_native_floorf(value); }
float fmaxf(float left,float right) { return r1_native_fmaxf(left,right); }
float expf(float value) { return r1_native_expf(value); }
float tanhf(float value) { return r1_native_tanhf(value); }
