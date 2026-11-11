/* Native0x7412c: SpO2 calibration polynomial. Float32 operation order is
 * intentional; the descriptor stores signed integer coefficients at8..24. */
#include <stdint.h>
float r1_goodix_spo2_quartic(float value,const int32_t *record)
{
    const volatile int32_t *p=record;
    float fourth=(float)p[2];
    float third=(float)p[3];
    fourth*=value;third*=value;
    fourth*=value;third*=value;
    fourth*=value;fourth*=value;
    fourth+=third*value;
    float second=(float)p[4];second*=value;
    fourth+=second*value;
    float first=(float)p[5];fourth+=first*value;
    float constant=(float)p[6];
    return (fourth+constant)/10000.0f;
}
