
undefined4 delay_us(undefined4 param_1)

{
  uint uVar1;
  undefined4 unaff_r7;
  uint in_fpscr;
  undefined4 uVar2;
  uint uVar3;
  float fVar4;
  
  uVar2 = VectorUnsignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
  uVar3 = VectorFloatToUnsignedFixed(uVar2,0x20,5);
  if ((*DAT_0041d218 & 0x1f) >> 3 == 2) {
    fVar4 = (float)VectorUnsignedToFloat(uVar3,(byte)(in_fpscr >> 0x16) & 3);
    fVar4 = (fVar4 * DAT_0041d210) / DAT_0041d214;
    uVar3 = (uint)(0.0 < fVar4) * (int)fVar4;
    uVar1 = 0x18;
  }
  else {
    uVar1 = 0xf;
  }
  if (uVar1 < uVar3) {
    func_0x00000040(uVar3 - uVar1);
  }
  return unaff_r7;
}

