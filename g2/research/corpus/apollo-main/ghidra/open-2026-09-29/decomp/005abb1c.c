
void af_warper_compute_line_best
               (int param_1,undefined4 param_2,int param_3,int param_4,int param_5,int param_6,
               int param_7,int param_8)

{
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int local_128 [65];
  
  for (iVar5 = 0; iVar5 < 0x41; iVar5 = iVar5 + 1) {
    local_128[iVar5] = 0;
  }
  iVar7 = param_4 - *(int *)(param_1 + 8);
  iVar6 = *(int *)(param_1 + 0x10);
  iVar5 = *(int *)(param_1 + 0x14);
  param_5 = param_5 - param_4;
  if (param_5 + iVar6 < *(int *)(param_1 + 0x18)) {
    iVar6 = *(int *)(param_1 + 0x18) - param_5;
  }
  if (*(int *)(param_1 + 0x1c) < param_5 + iVar5) {
    iVar5 = *(int *)(param_1 + 0x1c) - param_5;
  }
  iVar6 = iVar6 - *(int *)(param_1 + 8);
  iVar5 = iVar5 - *(int *)(param_1 + 8);
  if (((-1 < iVar6) && (iVar6 <= iVar5)) && (iVar5 < 0x41)) {
    for (iVar8 = 0; iVar8 < param_8; iVar8 = iVar8 + 1) {
      sVar1 = *(short *)(iVar8 * 0x2c + param_7 + 8);
      sVar2 = *(short *)(iVar8 * 0x2c + param_7 + 6);
      iVar3 = FT_MulFix((int)*(short *)(param_7 + iVar8 * 0x2c + 2),param_2);
      uVar4 = (iVar6 + param_3 + iVar3) - iVar7;
      for (iVar3 = iVar6; iVar3 <= iVar5; iVar3 = iVar3 + 1) {
        local_128[iVar3] =
             ((int)sVar1 - (int)sVar2) * *(int *)(DAT_005abc60 + (uVar4 & 0x3f) * 4) +
             local_128[iVar3];
        uVar4 = uVar4 + 1;
      }
    }
    for (; iVar6 <= iVar5; iVar6 = iVar6 + 1) {
      iVar8 = local_128[iVar6];
      iVar3 = (iVar6 + param_6) - iVar7;
      if ((*(int *)(param_1 + 0x34) < iVar8) ||
         ((iVar8 == *(int *)(param_1 + 0x34) && (iVar3 < *(int *)(param_1 + 0x38))))) {
        *(int *)(param_1 + 0x34) = iVar8;
        *(int *)(param_1 + 0x38) = iVar3;
        *(undefined4 *)(param_1 + 0x2c) = param_2;
        *(int *)(param_1 + 0x30) = (iVar6 + param_3) - iVar7;
      }
    }
  }
  return;
}

