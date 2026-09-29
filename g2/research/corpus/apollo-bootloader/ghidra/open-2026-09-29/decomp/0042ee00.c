
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint hw_channel_normalize_42ee00(uint param_1,char param_2)

{
  uint in_fpscr;
  float fVar1;
  
  if ((*_DAT_0042f178 != '\0') && (param_2 != '\0')) {
    fVar1 = (float)VectorUnsignedToFloat
                             (((param_1 & 0xfffff) >> 6) * 0x4a6 >> 0xc,(byte)(in_fpscr >> 0x16) & 3
                             );
    fVar1 = ((fVar1 / (1.0 - _DAT_0042f170[1]) + *_DAT_0042f170 * fRam0042f014) * fRam0042f018) /
            fRam0042f01c;
    param_1 = ((uint)(0.0 < fVar1) * (int)fVar1 & 0xfff) << 6 | param_1 & 0xfff00000;
  }
  return param_1;
}

