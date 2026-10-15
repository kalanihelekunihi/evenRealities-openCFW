/* Apollo Nema degree cosine/sine approximations at 0x524130 and 0x52405c. */
#include <stdint.h>

static float nema_cosine_phase(float phase) {
    const float two_pi=0x1.921fb6p+2f;
    const float minus_two_pi=-0x1.921fb6p+2f;
    const float pi=0x1.921fb6p+1f;
    const float minus_pi=-0x1.921fb6p+1f;
    const float half_pi=0x1.921fb8p+0f;
    int32_t sign=1;
    if (phase<0.0f) {
        const int32_t turns=(int32_t)(phase/minus_two_pi)+1;
        phase=(float)turns*two_pi-phase;
    }
    if (phase>=two_pi) {
        const int32_t turns=(int32_t)(phase/two_pi);
        phase-=(float)turns*two_pi;
    }
    if (phase>=pi) {phase+=minus_pi;sign=-1;}
    if (phase>=half_pi) {phase=pi-phase;sign=-sign;}
    const float square=phase*phase;
    const float inner=0x1.54b3b6p-5f-0x1.544a7p-10f*square;
    const float middle=-0.5f+inner*square;
    float result=1.0f+middle*square;
    if (result>=0x1.000002p+0f) result-=2.0f;
    return sign<1?-result:result;
}

float audio_uart_nema_cos_524130(float degrees)
    __attribute__((pcs("aapcs-vfp")));
float audio_uart_nema_sin_52405c(float degrees)
    __attribute__((pcs("aapcs-vfp")));

float audio_uart_nema_cos_524130(float degrees) {
    return nema_cosine_phase(degrees*0x1.1df46ap-6f);
}

float audio_uart_nema_sin_52405c(float degrees) {
    return nema_cosine_phase(-0x1.921fb6p+0f+
                             degrees*0x1.1df46ap-6f);
}
