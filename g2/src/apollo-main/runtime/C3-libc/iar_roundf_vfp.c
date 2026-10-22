/* IAR DLIB roundf VFP entry, stock 0x577d08..0x577d18, firmware 2.2.6.10.
 * Stock: vmov r0,s0; mov ip,lr; bl 0x577d18 (bit core); vmov s0,r0; bx ip.
 * The bit core 0x577d18 is audio_roundf (runtime/float-runtime/math.c),
 * declared pcs("aapcs") so its float argument and result travel in r0,
 * which is exactly the core's register contract. Callers (liblc3 spec.c and
 * the layout-4 watchface helpers) pass x in s0, so this entry is
 * pcs("aapcs-vfp") (the hard-float payload default). Compilation is not byte identity. */

extern __attribute__((pcs("aapcs"))) float audio_roundf(float input); /* Stock 0x00577D18 (roundf bit core) */

/* Stock 0x00577D08 (roundf VFP entry) */
__attribute__((pcs("aapcs-vfp"))) float roundf_577d08(float value)
{
    return audio_roundf(value);
}
