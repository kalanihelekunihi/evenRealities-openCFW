#ifndef G2_ANGLE_MODEL_H
#define G2_ANGLE_MODEL_H
#include <stdint.h>
/* Offline reconstruction for synthetic vectors; not firmware replacement. */
typedef struct { double angle_rad, delay_s, quality, max_rms; } G2AngleResult;
G2AngleResult g2_angle_model(const int16_t *left,const int16_t *right,int n,
                            int max_lag,double rms_floor,double quality_floor);
/* Assumed physical constants from stock literals; not measured dimensions. */
#define G2_ANGLE_SAMPLE_RATE 16000.0
#define G2_ANGLE_SPACING 0.14
#define G2_ANGLE_SPEED 343.0
#endif
