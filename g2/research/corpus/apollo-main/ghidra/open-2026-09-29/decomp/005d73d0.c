
void FUN_005d73d0(int *param_1,int param_2,int param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int *piVar10;
  uint local_40;
  int local_3c;
  int local_38;
  undefined4 local_34;
  int local_30;
  int *piStack_2c;
  int local_28;
  
  iVar2 = param_2 + param_3 * 0xcc;
  local_30 = iVar2 + 4;
  local_34 = *(undefined4 *)(iVar2 + 200);
  iVar2 = *(int *)(iVar2 + 0xcc);
  if ((int)((uint)*(byte *)(param_1 + 4) << 0x1c) < 0) {
    return;
  }
  piStack_2c = param_1;
  local_28 = param_2;
  iVar3 = FT_MulFix(*param_1,local_34);
  uVar9 = iVar2 + iVar3;
  iVar2 = FT_MulFix(param_1[1],local_34);
  if (((param_3 == 0) && (*(char *)(param_4 + 0x78) == '\0')) ||
     ((param_3 == 1 && (*(char *)(param_4 + 0x79) == '\0')))) {
    param_1[2] = uVar9;
    param_1[3] = iVar2;
    param_1[4] = param_1[4] | 8;
    return;
  }
  if (((param_3 == 0) && (*(char *)(param_4 + 0x7a) != '\0')) ||
     ((param_3 == 1 && (*(char *)(param_4 + 0x7b) != '\0')))) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  param_1[3] = iVar2;
  local_40 = 0;
  local_3c = 0;
  local_38 = 0;
  if (param_3 == 1) {
    FUN_005d8828(local_28 + 0x19c,param_1[1] + *param_1,*param_1,&local_40);
  }
  if (local_40 == 1) {
    param_1[2] = local_3c - iVar2;
  }
  else if (local_40 == 0) {
LAB_005d74b4:
    piVar10 = (int *)param_1[5];
    iVar3 = iVar2 >> 1;
    if (piVar10 != (int *)0x0) {
      if (-1 < (int)((uint)*(byte *)(piVar10 + 4) << 0x1c)) {
        FUN_005d73d0(piVar10,local_28,param_3,param_4);
      }
      iVar8 = piVar10[2];
      iVar7 = piVar10[3];
      iVar4 = FT_MulFix((*param_1 + (param_1[1] >> 1)) - (*piVar10 + (piVar10[1] >> 1)),local_34);
      uVar9 = (iVar4 + iVar8 + (iVar7 >> 1)) - iVar3;
    }
    param_1[2] = uVar9;
    param_1[3] = iVar2;
    uVar6 = uVar9;
    if (*(char *)(param_4 + 0x7c) != '\0') {
      if (iVar2 < 0x41) {
        if (iVar2 < 0x20) {
          if (iVar2 < 1) {
            uVar6 = uVar9 + 0x20 & 0xffffffc0;
          }
          else {
            uVar5 = uVar9 + 0x20 & 0xffffffc0;
            uVar6 = iVar2 + uVar9 + 0x20 & 0xffffffc0;
            iVar3 = uVar5 - uVar9;
            iVar4 = (uVar6 - uVar9) - iVar2;
            if (iVar3 < 0) {
              iVar3 = -iVar3;
            }
            if (iVar4 < 0) {
              iVar4 = -iVar4;
            }
            if (iVar3 <= iVar4) {
              uVar6 = uVar5;
            }
          }
        }
        else {
          iVar2 = 0x40;
          uVar6 = uVar9 + iVar3 & 0xffffffc0;
        }
      }
      else {
        iVar2 = FUN_005d7340(local_30,iVar2,0);
      }
    }
    iVar3 = FUN_005d739c(uVar6,iVar2);
    param_1[2] = iVar3 + uVar6;
    param_1[3] = iVar2;
  }
  else if (local_40 == 3) {
    param_1[2] = local_38;
    param_1[3] = local_3c - local_38;
  }
  else {
    if (2 < local_40) goto LAB_005d74b4;
    param_1[2] = local_38;
  }
  if (bVar1) {
    if (param_1[3] < 0x40) {
      uVar9 = 0x40;
    }
    else {
      uVar9 = param_1[3] + 0x20U & 0xffffffc0;
    }
    if (local_40 == 1) {
      param_1[2] = local_3c - uVar9;
      param_1[3] = uVar9;
    }
    else {
      if (local_40 != 0) {
        if (local_40 == 3) goto LAB_005d75e0;
        if (local_40 < 3) {
          param_1[3] = uVar9;
          goto LAB_005d75e0;
        }
      }
      param_1[3] = uVar9;
      iVar2 = (int)uVar9 >> 1;
      if ((int)(uVar9 << 0x19) < 0) {
        uVar6 = (param_1[2] + iVar2 & 0xffffffc0U) + 0x20;
      }
      else {
        uVar6 = param_1[2] + iVar2 + 0x20U & 0xffffffc0;
      }
      param_1[2] = uVar6 - iVar2;
      param_1[3] = uVar9;
    }
  }
LAB_005d75e0:
  param_1[4] = param_1[4] | 8;
  return;
}

