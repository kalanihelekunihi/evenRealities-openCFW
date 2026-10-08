#include <stdint.h>
/* Reconstructed 0x5A1E8C. Celsius meaning corroborated by pinned public SPOT source; no sensor calibration proof. */
uint32_t audio_platform_classify(float value) {
    if(value>=-273.0f && value<-20.0f) return 0;
    if(value>=-20.0f && value<0.0f) return 1;
    if(value>=0.0f && value<50.0f) return 2;
    if(value>=50.0f && value<1000.0f) return 3;
    return 4;
}
