
float FUN_0052405c(float param_1)

{
  uint uVar1;
  int iVar2;
  uint in_fpscr;
  float fVar3;
  float fVar4;
  
  fVar3 = DAT_00524200 + param_1 * DAT_005241fc;
  if (fVar3 < 0.0) {
    fVar4 = (float)VectorSignedToFloat((int)(fVar3 / DAT_0052412c) + 1,
                                       (byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    fVar3 = fVar4 * DAT_00524128 - fVar3;
  }
  uVar1 = in_fpscr & 0xfffffff | (uint)(fVar3 < DAT_00524128) << 0x1f;
  if (SUB41(uVar1 >> 0x1f,0) == (NAN(fVar3) || NAN(DAT_00524128))) {
    fVar4 = (float)VectorSignedToFloat((int)(fVar3 / DAT_00524128),(byte)(uVar1 >> 0x16) & 3);
    fVar3 = fVar3 - fVar4 * DAT_00524128;
  }
  iVar2 = 1;
  if (DAT_00524204 <= fVar3) {
    iVar2 = -1;
    fVar3 = fVar3 + DAT_00524208;
  }
  if (DAT_0052420c <= fVar3) {
    fVar3 = DAT_00524204 - fVar3;
    iVar2 = -iVar2;
  }
  fVar3 = fVar3 * fVar3;
  fVar3 = ((DAT_00524214 - fVar3 * DAT_00524210) * fVar3 + -0.5) * fVar3 + 1.0;
  if (DAT_005241f8 <= fVar3) {
    fVar3 = fVar3 + -2.0;
  }
  if (iVar2 < 1) {
    fVar3 = -fVar3;
  }
  return fVar3;
}

