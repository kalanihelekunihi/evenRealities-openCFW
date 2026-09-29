
float FUN_0059b714(int param_1)

{
  int iVar1;
  int iVar2;
  bool bVar3;
  bool bVar4;
  float fVar5;
  
  fVar5 = 1.0;
  for (; param_1 < 0; param_1 = param_1 + 0x1c) {
    fVar5 = fVar5 * DAT_0059b808;
  }
  if (0x1b < param_1) {
    do {
      iVar1 = param_1 + -0x1c;
      fVar5 = fVar5 * 10.0;
      iVar2 = param_1 + -0x38;
      if (0x1b < iVar1) {
        iVar1 = param_1 + -0x38;
        fVar5 = fVar5 * 10.0;
        iVar2 = param_1 + -0x54;
      }
      bVar4 = SBORROW4(iVar1,0x1c);
      bVar3 = iVar2 < 0;
      iVar2 = iVar1;
      if (bVar3 == bVar4) {
        iVar2 = iVar1 + -0x1c;
        fVar5 = fVar5 * 10.0;
        bVar4 = SBORROW4(iVar2,0x1c);
        bVar3 = iVar1 + -0x38 < 0;
      }
      param_1 = iVar2;
      if (bVar3 == bVar4) {
        param_1 = iVar2 + -0x1c;
        fVar5 = fVar5 * 10.0;
        bVar4 = SBORROW4(param_1,0x1c);
        bVar3 = iVar2 + -0x38 < 0;
      }
    } while (bVar3 == bVar4);
  }
  return fVar5 * *(float *)(DAT_0059c174 + param_1 * 4 + 0xd4);
}

