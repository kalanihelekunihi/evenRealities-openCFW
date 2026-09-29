
int FUN_00585258(byte *param_1,byte *param_2,undefined4 *param_3,int *param_4,int param_5)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  byte bVar5;
  int iVar6;
  byte *pbVar7;
  int iVar8;
  char acStack_59 [49];
  byte *local_28;
  
  bVar1 = false;
  param_5 = param_5 * 9;
  iVar8 = 0;
  if (0x2d < param_5) {
    param_5 = 0x2d;
  }
  *param_4 = 0;
  param_4[1] = 0;
  bVar2 = false;
  for (; *param_2 == 0x30; param_2 = param_2 + 1) {
    bVar2 = true;
  }
  iVar6 = 0;
  local_28 = param_1;
  for (; *param_2 - 0x30 < 10; param_2 = param_2 + 1) {
    if (iVar6 < param_5) {
      acStack_59[iVar6 + 1] = *param_2 - 0x30;
      iVar6 = iVar6 + 1;
    }
    else {
      *param_4 = *param_4 + 1;
      if (*param_2 != 0x30) {
        bVar1 = true;
      }
    }
    bVar2 = true;
  }
  iVar3 = FUN_004d43a8();
  if (*param_2 == **(byte **)(iVar3 + 0x24)) {
    param_2 = param_2 + 1;
  }
  if (iVar6 == 0) {
    for (; *param_2 == 0x30; param_2 = param_2 + 1) {
      *param_4 = *param_4 + -1;
      bVar2 = true;
    }
  }
  while( true ) {
    bVar5 = *param_2;
    if (9 < bVar5 - 0x30) break;
    if (iVar6 < param_5) {
      acStack_59[iVar6 + 1] = bVar5 - 0x30;
      iVar6 = iVar6 + 1;
      *param_4 = *param_4 + -1;
    }
    else if (bVar5 != 0x30) {
      bVar1 = true;
    }
    param_2 = param_2 + 1;
    bVar2 = true;
  }
  if (bVar1) {
    acStack_59[param_5] = acStack_59[param_5] + '\x01';
  }
  for (; 0 < iVar6; iVar6 = iVar6 + -1) {
    if (acStack_59[iVar6] != '\0') goto LAB_00585342;
    *param_4 = *param_4 + 1;
  }
  if (iVar6 == 0) {
    acStack_59[1] = 0;
    iVar6 = 1;
  }
LAB_00585342:
  pbVar7 = param_2;
  if (bVar2) {
    iVar4 = (iVar6 / 9) * 9 + (9 - iVar6);
    iVar3 = 0;
    if (iVar4 != (iVar4 / 9) * 9) {
      iVar8 = 1;
    }
    for (; iVar3 < iVar6; iVar3 = iVar3 + 1) {
      if (iVar4 == (iVar4 / 9) * 9) {
        iVar8 = iVar8 + 1;
        param_4[iVar8] = (uint)(byte)acStack_59[iVar3 + 1];
      }
      else {
        param_4[iVar8] = (uint)(byte)acStack_59[iVar3 + 1] + param_4[iVar8] * 10;
      }
      iVar4 = iVar4 + 1;
    }
    if ((*param_2 | 0x20) == 0x65) {
      pbVar7 = param_2 + 1;
      if (*pbVar7 == 0x2b || *pbVar7 == 0x2d) {
        bVar5 = *pbVar7;
        pbVar7 = param_2 + 2;
      }
      else {
        bVar5 = 0x2b;
      }
      bVar1 = false;
      iVar6 = 0;
      for (; *pbVar7 - 0x30 < 10; pbVar7 = pbVar7 + 1) {
        if (iVar6 < DAT_0058540c) {
          iVar6 = (uint)*pbVar7 + iVar6 * 10 + -0x30;
        }
        bVar1 = true;
      }
      if (bVar5 == 0x2d) {
        iVar6 = -iVar6;
      }
      *param_4 = iVar6 + *param_4;
      if (!bVar1) {
        pbVar7 = param_2;
      }
    }
  }
  if (param_3 != (undefined4 *)0x0) {
    if (!bVar2) {
      pbVar7 = local_28;
    }
    *param_3 = pbVar7;
  }
  return iVar8;
}

