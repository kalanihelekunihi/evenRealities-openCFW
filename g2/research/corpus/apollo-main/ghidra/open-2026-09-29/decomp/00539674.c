
int FUN_00539674(int param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  byte bVar5;
  uint in_fpscr;
  float fVar6;
  float fVar7;
  
  fVar6 = (float)VectorUnsignedToFloat(param_2,(byte)(in_fpscr >> 0x16) & 3);
  fVar7 = (float)VectorUnsignedToFloat(param_3,(byte)(in_fpscr >> 0x16) & 3);
  fVar6 = (float)FUN_0053937c(fVar7 / DAT_00539940,fVar6 / DAT_00539940);
  if ((fVar6 < 1.0) &&
     (uVar2 = (int)((ulonglong)param_2 / ((ulonglong)param_2 / (ulonglong)DAT_00539d88)) * 10,
     param_4 < uVar2)) {
    param_4 = uVar2;
  }
  if (param_3 < param_4) {
    uVar2 = param_4 / param_3;
    if (param_4 != param_3 * (param_4 / param_3)) {
      uVar2 = uVar2 + 1;
    }
    if (0x31 < uVar2) {
      return 5;
    }
    bVar4 = *(byte *)(DAT_00539d8c + uVar2) & 0xf;
    bVar5 = *(byte *)(DAT_00539d8c + uVar2) >> 4;
    iVar1 = (uint)bVar4 * (uint)bVar5;
  }
  else {
    iVar1 = 1;
    bVar5 = 1;
    bVar4 = 1;
  }
  fVar6 = (float)VectorUnsignedToFloat(iVar1 * param_3,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
  fVar7 = (float)VectorUnsignedToFloat(param_2,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
  iVar1 = FUN_005395a0(fVar7 / DAT_00539940,fVar6 / DAT_00539940,param_1);
  if (iVar1 == 0) {
    uVar2 = DAT_00539d90;
    if (*(char *)(param_1 + 2) == '\0') {
      uVar2 = DAT_00539d88;
    }
    uVar3 = param_2 / *(byte *)(param_1 + 3);
    if (param_2 != (uint)*(byte *)(param_1 + 3) * (param_2 / *(byte *)(param_1 + 3))) {
      uVar3 = uVar3 + 1;
    }
    if (uVar3 < uVar2) {
      iVar1 = 5;
    }
    else {
      *(byte *)(param_1 + 4) = bVar5;
      *(byte *)(param_1 + 5) = bVar4;
    }
  }
  return iVar1;
}

