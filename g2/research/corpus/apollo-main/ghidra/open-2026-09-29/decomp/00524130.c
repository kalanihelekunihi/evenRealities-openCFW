
float FUN_00524130(float param_1)

{
  uint uVar1;
  int iVar2;
  uint in_fpscr;
  float fVar3;
  
  param_1 = param_1 * DAT_005241fc;
  if (param_1 < 0.0) {
    fVar3 = (float)VectorSignedToFloat((int)(param_1 / DAT_0052425c) + 1,
                                       (byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    param_1 = fVar3 * DAT_00524258 - param_1;
  }
  uVar1 = in_fpscr & 0xfffffff | (uint)(param_1 < DAT_00524258) << 0x1f;
  if (SUB41(uVar1 >> 0x1f,0) == (NAN(param_1) || NAN(DAT_00524258))) {
    fVar3 = (float)VectorSignedToFloat((int)(param_1 / DAT_00524258),(byte)(uVar1 >> 0x16) & 3);
    param_1 = param_1 - fVar3 * DAT_00524258;
  }
  iVar2 = 1;
  if (DAT_00524204 <= param_1) {
    iVar2 = -1;
    param_1 = param_1 + DAT_00524208;
  }
  if (DAT_0052420c <= param_1) {
    param_1 = DAT_00524204 - param_1;
    iVar2 = -iVar2;
  }
  param_1 = param_1 * param_1;
  fVar3 = ((DAT_00524214 - param_1 * DAT_00524210) * param_1 + -0.5) * param_1 + 1.0;
  if (DAT_005242e4 <= fVar3) {
    fVar3 = fVar3 + -2.0;
  }
  if (iVar2 < 1) {
    fVar3 = -fVar3;
  }
  return fVar3;
}

