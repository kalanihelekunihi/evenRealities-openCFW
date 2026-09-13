/* SPDX-License-Identifier: MIT */
/* Recovered dispatcher at package 0x478a4; upstream descriptor ABI. */
#include "fft_types.h"
extern void backup_cfft(const csky_vdsp2_cfft_instance_q15 *,q15_t *,unsigned,unsigned);
extern void backup_split_forward(q15_t *,unsigned,q15_t *,q15_t *,unsigned);
extern void backup_split_inverse(q15_t *,unsigned,q15_t *,q15_t *,unsigned);
void open_cfw_gx8002_backup_rfft(const volatile csky_vdsp2_rfft_instance_q15 *state,
                               q15_t *input,q15_t *output)
{
    unsigned inverse=state->ifftFlagR;
    unsigned half=state->fftLenReal>>1;
    const csky_vdsp2_cfft_instance_q15 *complex=state->pCfft;
    if (inverse!=1) {
        backup_cfft(complex,input,inverse,state->bitReverseFlagR);
        unsigned modifier=state->twidCoefRModifier;
        q15_t *coefficients=state->pTwiddleAReal;
        backup_split_forward(input,half,coefficients,output,modifier);
    } else {
        unsigned modifier=state->twidCoefRModifier;
        q15_t *coefficients=state->pTwiddleAReal;
        backup_split_inverse(input,half,coefficients,output,modifier);
        unsigned reversal=state->bitReverseFlagR;
        inverse=state->ifftFlagR;
        backup_cfft(complex,output,inverse,reversal);
        unsigned length=state->fftLenReal;
        for (unsigned i=0;i<length;i++)
            output[i]=(q15_t)((uint16_t)output[i]*2u);
    }
}
