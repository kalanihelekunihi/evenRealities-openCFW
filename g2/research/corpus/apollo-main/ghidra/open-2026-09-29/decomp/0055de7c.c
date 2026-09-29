
uint FUN_0055de7c(uint param_1,char param_2)

{
  uint in_fpscr;
  float fVar1;
  
  if ((*DAT_0055e1f4 != '\0') && (param_2 != '\0')) {
    fVar1 = (float)VectorUnsignedToFloat
                             (((param_1 & 0xfffff) >> 6) * 0x4a6 >> 0xc,(byte)(in_fpscr >> 0x16) & 3
                             );
    fVar1 = ((fVar1 / (1.0 - DAT_0055e1ec[1]) + *DAT_0055e1ec * DAT_0055e090) * DAT_0055e094) /
            DAT_0055e098;
    param_1 = ((uint)(0.0 < fVar1) * (int)fVar1 & 0xfff) << 6 | param_1 & 0xfff00000;
  }
  return param_1;
}

