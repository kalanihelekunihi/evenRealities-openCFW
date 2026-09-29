
int FUN_00585410(byte *param_1,byte *param_2,undefined4 *param_3,int *param_4,int param_5)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  byte bVar5;
  int iVar6;
  byte *pbVar7;
  int iVar8;
  undefined4 local_54;
  byte local_50 [40];
  byte *local_28;
  
  param_5 = param_5 * 7;
  iVar8 = 0;
  if (0x23 < param_5) {
    param_5 = 0x23;
  }
  *param_4 = 0;
  param_4[1] = 0;
  bVar1 = false;
  for (; *param_2 == 0x30; param_2 = param_2 + 1) {
    bVar1 = true;
  }
  local_54 = s_0123456789abcdefABCDEF_005855e8;
  iVar6 = 0;
  local_28 = param_1;
  while (iVar3 = FUN_004d40e0(s_0123456789abcdefABCDEF_005855e8,*param_2,0x16), iVar3 != 0) {
    if (param_5 < iVar6) {
      *param_4 = *param_4 + 1;
    }
    else {
      local_50[iVar6] = (&LAB_00585600)[iVar3 - (int)local_54];
      iVar6 = iVar6 + 1;
    }
    param_2 = param_2 + 1;
    bVar1 = true;
  }
  iVar3 = FUN_004d43a8();
  if (*param_2 == **(byte **)(iVar3 + 0x24)) {
    param_2 = param_2 + 1;
  }
  if (iVar6 == 0) {
    for (; *param_2 == 0x30; param_2 = param_2 + 1) {
      *param_4 = *param_4 + -1;
      bVar1 = true;
    }
  }
  while (iVar3 = FUN_004d40e0(s_0123456789abcdefABCDEF_005855e8,*param_2,0x16), iVar3 != 0) {
    if (iVar6 <= param_5) {
      local_50[iVar6] = (&LAB_00585600)[iVar3 - (int)local_54];
      iVar6 = iVar6 + 1;
      *param_4 = *param_4 + -1;
    }
    param_2 = param_2 + 1;
    bVar1 = true;
  }
  if (param_5 < iVar6) {
    if (7 < local_50[param_5]) {
      local_50[param_5 + -1] = local_50[param_5 + -1] + 1;
    }
    *param_4 = *param_4 + 1;
    iVar6 = param_5;
  }
  for (; 0 < iVar6; iVar6 = iVar6 + -1) {
    if (local_50[iVar6 + -1] != 0) goto LAB_00585516;
    *param_4 = *param_4 + 1;
  }
  if (iVar6 == 0) {
    local_50[0] = 0;
    iVar6 = 1;
  }
LAB_00585516:
  *param_4 = *param_4 << 2;
  pbVar7 = param_2;
  if (bVar1) {
    iVar4 = (iVar6 / 7) * 7 + (7 - iVar6);
    iVar3 = 0;
    if (iVar4 != (iVar4 / 7) * 7) {
      iVar8 = 1;
    }
    for (; iVar3 < iVar6; iVar3 = iVar3 + 1) {
      if (iVar4 == (iVar4 / 7) * 7) {
        iVar8 = iVar8 + 1;
        param_4[iVar8] = (uint)local_50[iVar3];
      }
      else {
        param_4[iVar8] = (uint)local_50[iVar3] + param_4[iVar8] * 0x10;
      }
      iVar4 = iVar4 + 1;
    }
    if ((*param_2 | 0x20) == 0x70) {
      pbVar7 = param_2 + 1;
      if (*pbVar7 == 0x2b || *pbVar7 == 0x2d) {
        bVar5 = *pbVar7;
        pbVar7 = param_2 + 2;
      }
      else {
        bVar5 = 0x2b;
      }
      bVar2 = false;
      iVar6 = 0;
      for (; *pbVar7 - 0x30 < 10; pbVar7 = pbVar7 + 1) {
        if (iVar6 < DAT_005855e4) {
          iVar6 = (uint)*pbVar7 + iVar6 * 10 + -0x30;
        }
        bVar2 = true;
      }
      if (bVar5 == 0x2d) {
        iVar6 = -iVar6;
      }
      *param_4 = iVar6 + *param_4;
      if (!bVar2) {
        pbVar7 = param_2;
      }
    }
  }
  if (param_3 != (undefined4 *)0x0) {
    if (!bVar1) {
      pbVar7 = local_28;
    }
    *param_3 = pbVar7;
  }
  return iVar8;
}

