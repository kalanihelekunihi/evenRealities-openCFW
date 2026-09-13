/* SPDX-License-Identifier: MIT */
/* Recovered dispatcher at package 0x47b14, using the upstream descriptor ABI. */
#include "fft_types.h"
extern void backup_radix4(q15_t *,unsigned,const q15_t *,unsigned);
extern void backup_radix4_inverse(q15_t *,unsigned,const q15_t *,unsigned);
extern void backup_radix4_by2(q15_t *,unsigned,const q15_t *);
extern void backup_radix4_by2_inverse(q15_t *,unsigned,const q15_t *);
extern void backup_bit_reverse(q15_t *,unsigned,const uint16_t *);
void open_cfw_gx8002_backup_cfft(const volatile csky_vdsp2_cfft_instance_q15 *state,
                               q15_t *samples,unsigned inverse,unsigned reversal)
{
    unsigned length=state->fftLen;
    switch (length) {
    case 16: case 64: case 256: case 1024: case 4096:
        if (inverse==1) backup_radix4_inverse(samples,length,state->pTwiddle,1);
        else backup_radix4(samples,length,state->pTwiddle,1);
        break;
    case 32: case 128: case 512: case 2048:
        if (inverse==1) backup_radix4_by2_inverse(samples,length,state->pTwiddle);
        else backup_radix4_by2(samples,length,state->pTwiddle);
        break;
    }
    if (reversal) {
        const uint16_t *table=state->pBitRevTable;
        unsigned entries=state->bitRevLength;
        backup_bit_reverse(samples,entries,table);
    }
}
