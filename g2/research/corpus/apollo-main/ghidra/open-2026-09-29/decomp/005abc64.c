
void af_warper_compute(uint *param_1,int param_2,byte param_3,uint *param_4,uint *param_5)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int local_38;
  
  if (param_3 == 1) {
    uVar7 = *(uint *)(param_2 + 0xc);
    uVar9 = *(uint *)(param_2 + 0x10);
  }
  else {
    uVar7 = *(uint *)(param_2 + 4);
    uVar9 = *(uint *)(param_2 + 8);
  }
  param_1[0xb] = uVar7;
  param_1[0xc] = uVar9;
  param_1[0xd] = 0x80000000;
  param_1[0xe] = 0;
  iVar1 = param_2 + (uint)param_3 * 0x544;
  uVar3 = *(undefined4 *)(iVar1 + 0x34);
  iVar1 = *(int *)(iVar1 + 0x2c);
  iVar2 = *(int *)(param_2 + 0x1c);
  iVar4 = *(int *)(param_2 + 0x18);
  *param_4 = uVar7;
  *param_5 = uVar9;
  if (0 < iVar1) {
    iVar8 = (int)*(short *)(iVar2 + 0xc);
    local_38 = iVar8;
    for (iVar5 = 1; iVar5 < iVar4; iVar5 = iVar5 + 1) {
      iVar6 = (int)*(short *)(iVar5 * 0x28 + iVar2 + 0xc);
      if (iVar6 < local_38) {
        local_38 = iVar6;
      }
      if (iVar8 < iVar6) {
        iVar8 = iVar6;
      }
    }
    if (local_38 < iVar8) {
      iVar2 = FT_MulFix(local_38,uVar7);
      *param_1 = uVar9 + iVar2;
      iVar2 = FT_MulFix(iVar8,uVar7);
      param_1[1] = uVar9 + iVar2;
      param_1[2] = *param_1 & 0xffffffc0;
      param_1[3] = param_1[1] + 0x3f & 0xffffffc0;
      param_1[4] = *param_1 & 0xffffffe0;
      param_1[5] = param_1[4] + 0x20;
      param_1[6] = param_1[1] & 0xffffffe0;
      param_1[7] = param_1[6] + 0x20;
      if ((int)param_1[1] < (int)param_1[5]) {
        param_1[5] = param_1[1];
      }
      if ((int)param_1[6] < (int)*param_1) {
        param_1[6] = *param_1;
      }
      param_1[8] = param_1[1] - *param_1;
      if ((int)param_1[8] < 0x41) {
        param_1[5] = *param_1;
        param_1[6] = param_1[1];
      }
      param_1[9] = param_1[6] - param_1[5];
      param_1[10] = param_1[7] - param_1[4];
      iVar2 = 0x10;
      if (((int)param_1[8] < 0x81) && (iVar2 = 8, (int)param_1[8] < 0x61)) {
        iVar2 = 4;
      }
      if ((int)param_1[9] < (int)(param_1[8] - iVar2)) {
        param_1[9] = param_1[8] - iVar2;
      }
      if ((int)(iVar2 + param_1[8]) < (int)param_1[10]) {
        param_1[10] = iVar2 + param_1[8];
      }
      if ((int)param_1[9] < (int)(param_1[8] * 3) / 4) {
        param_1[9] = (int)(param_1[8] * 3) / 4;
      }
      if ((int)(param_1[8] * 5) / 4 < (int)param_1[10]) {
        param_1[10] = (int)(param_1[8] * 5) / 4;
      }
      for (uVar9 = param_1[9]; (int)uVar9 <= (int)param_1[10]; uVar9 = uVar9 + 1) {
        uVar10 = param_1[1];
        if ((int)uVar9 < (int)param_1[8]) {
          uVar11 = param_1[8] + (*param_1 - uVar9);
          if ((int)param_1[5] < (int)uVar11) {
            uVar10 = param_1[5] + (uVar10 - uVar11);
            uVar11 = param_1[5];
          }
        }
        else {
          uVar11 = param_1[8] + (*param_1 - uVar9);
          if ((int)uVar11 < (int)param_1[4]) {
            uVar10 = (param_1[4] + uVar10) - uVar11;
            uVar11 = param_1[4];
          }
        }
        if ((int)uVar11 < (int)*param_1) {
          iVar2 = *param_1 - uVar11;
        }
        else {
          iVar2 = uVar11 - *param_1;
        }
        if ((int)uVar10 < (int)param_1[1]) {
          iVar2 = (param_1[1] + iVar2) - uVar10;
        }
        else {
          iVar2 = (uVar10 + iVar2) - param_1[1];
        }
        iVar4 = FT_DivFix(uVar9 - param_1[8],iVar8 - local_38);
        iVar5 = FT_MulFix(local_38,iVar4 + uVar7);
        af_warper_compute_line_best
                  (param_1,iVar4 + uVar7,uVar11 - iVar5,uVar11,uVar10,iVar2 * 10,uVar3,iVar1);
      }
      uVar10 = param_1[0xb];
      uVar9 = param_1[0xc];
      iVar1 = FT_MulFix(local_38,uVar10 - uVar7);
      *(uint *)(param_2 + 0xac0) = uVar9 + iVar1;
      iVar1 = FT_MulFix(iVar8,uVar10 - uVar7);
      *(uint *)(param_2 + 0xac4) = uVar9 + iVar1;
      *param_4 = uVar10;
      *param_5 = uVar9;
    }
  }
  return;
}

