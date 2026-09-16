// SPDX-License-Identifier: MIT
// Package 0x4766c..0x476bc: final DRC-stage gain setter.
extern float open_cfw_gx8002_powf(float, float);
int open_cfw_gx8002_drc_stage4_set_gain(float *memory, float gain_db)
{
    volatile float *s = memory;
    if (gain_db > 0.0f)
        return -1;
    if (gain_db < -80.0f) {
        s[15] = 0.0f;
        return 0;
    }
    s[4] = gain_db;
    s[15] = open_cfw_gx8002_powf(10.0f, gain_db / 20.0f);
    return 0;
}
