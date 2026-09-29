
void FUN_005d2418(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int *local_40;
  uint local_3c;
  int local_38;
  int local_34;
  uint local_30;
  int local_2c;
  uint local_28;
  uint local_24;
  undefined4 uStack_20;
  
  uVar6 = *(undefined4 *)(param_2 + 0xb0);
  iVar5 = 0;
  uStack_20 = param_4;
  FUN_0043c0e4(param_1,0x134,0);
  *param_1 = *(int *)(param_2 + 0x34);
  FUN_005d328a(uVar6,param_1 + 3,param_1 + 4,param_1 + 5);
  FUN_005d32c0(uVar6,&local_3c,&local_40);
  FUN_005d32d4(uVar6,&local_24,&local_34);
  FUN_005d32e8(uVar6,&local_30,&local_38);
  FUN_005d32fe(uVar6,&local_28,&local_2c);
  iVar2 = DAT_005d3014;
  iVar1 = FUN_005d3314(uVar6);
  if ((iVar1 == 1) &&
     ((local_3c == 0 ||
      ((((local_3c == 4 && (*local_40 * 0x10000 < iVar2)) && (local_40[1] * 0x10000 < iVar2)) &&
       ((0x3700000 < local_40[2] * 0x10000 && (0x3700000 < local_40[3] * 0x10000)))))))) {
    param_1[0xe] = iVar2 + -1;
    iVar2 = FT_MulFix(param_1[0xe],*param_1);
    param_1[0xf] = (iVar2 + 0x8000U & 0xffff0000) - 0x8000;
    param_1[0x10] = *param_1;
    param_1[0xc] = 0x31;
    param_1[9] = *(int *)(param_2 + 0xe8) * 2 + 0x3700001;
    iVar2 = FT_MulFix(param_1[9],*param_1);
    param_1[10] = (iVar2 + 0x8000U & 0xffff0000) + 0x8000;
    param_1[0xb] = *param_1;
    param_1[7] = 0x32;
    *(undefined1 *)((int)param_1 + 9) = 1;
  }
  else {
    for (uVar3 = 0; uVar3 < local_3c; uVar3 = uVar3 + 2) {
      param_1[param_1[1] * 5 + 0x11] = local_40[uVar3] << 0x10;
      param_1[param_1[1] * 5 + 0x12] = local_40[uVar3 + 1] << 0x10;
      iVar2 = param_1[param_1[1] * 5 + 0x12] - param_1[param_1[1] * 5 + 0x11];
      if (-1 < iVar2) {
        if (iVar5 < iVar2) {
          iVar5 = iVar2;
        }
        if (uVar3 == 0) {
          *(undefined1 *)(param_1 + param_1[1] * 5 + 0x15) = 1;
          param_1[param_1[1] * 5 + 0x13] = param_1[param_1[1] * 5 + 0x12];
        }
        else {
          param_1[param_1[1] * 5 + 0x12] =
               param_1[param_1[1] * 5 + 0x12] + *(int *)(param_2 + 0xe8) * 2;
          param_1[param_1[1] * 5 + 0x11] =
               param_1[param_1[1] * 5 + 0x11] + *(int *)(param_2 + 0xe8) * 2;
          *(undefined1 *)(param_1 + param_1[1] * 5 + 0x15) = 0;
          param_1[param_1[1] * 5 + 0x13] = param_1[param_1[1] * 5 + 0x11];
        }
        param_1[1] = param_1[1] + 1;
      }
    }
    for (uVar3 = 0; uVar3 < local_24; uVar3 = uVar3 + 2) {
      param_1[param_1[1] * 5 + 0x11] = *(int *)(local_34 + uVar3 * 4) << 0x10;
      param_1[param_1[1] * 5 + 0x12] = *(int *)(local_34 + uVar3 * 4 + 4) << 0x10;
      iVar2 = param_1[param_1[1] * 5 + 0x12] - param_1[param_1[1] * 5 + 0x11];
      if (-1 < iVar2) {
        if (iVar5 < iVar2) {
          iVar5 = iVar2;
        }
        *(undefined1 *)(param_1 + param_1[1] * 5 + 0x15) = 1;
        param_1[param_1[1] * 5 + 0x13] = param_1[param_1[1] * 5 + 0x12];
        param_1[1] = param_1[1] + 1;
      }
    }
    iVar2 = FT_DivFix(0x10000,*param_1);
    for (uVar3 = 0; uVar3 < (uint)param_1[1]; uVar3 = uVar3 + 1) {
      iVar1 = param_1[uVar3 * 5 + 0x13];
      if ((char)param_1[uVar3 * 5 + 0x15] == '\0') {
        iVar8 = 0x7fffffff;
        for (uVar9 = 2; uVar9 < local_30; uVar9 = uVar9 + 2) {
          iVar4 = *(int *)(local_38 + uVar9 * 4) * 0x10000 + *(int *)(param_2 + 0xe8) * 2;
          if (iVar1 - iVar4 < 0) {
            iVar7 = iVar4 - iVar1;
          }
          else {
            iVar7 = iVar1 - iVar4;
          }
          if (((iVar7 < iVar8) && (iVar7 < iVar2)) &&
             (param_1[uVar3 * 5 + 0x13] = iVar4, iVar8 = iVar7, iVar7 == 0)) break;
        }
      }
      else {
        iVar8 = 0x7fffffff;
        for (uVar9 = 0; iVar4 = iVar8, uVar9 < local_28; uVar9 = uVar9 + 2) {
          iVar7 = *(int *)(local_2c + uVar9 * 4 + 4);
          if (iVar1 + iVar7 * -0x10000 < 0) {
            iVar4 = iVar7 * 0x10000 - iVar1;
          }
          else {
            iVar4 = iVar1 + iVar7 * -0x10000;
          }
          if (((iVar4 < iVar8) && (iVar4 < iVar2)) &&
             (param_1[uVar3 * 5 + 0x13] = iVar7 * 0x10000, iVar8 = iVar4, iVar4 == 0)) break;
        }
        if (1 < local_30) {
          iVar8 = *(int *)(local_38 + 4);
          if (iVar1 + iVar8 * -0x10000 < 0) {
            iVar1 = iVar8 * 0x10000 - iVar1;
          }
          else {
            iVar1 = iVar1 + iVar8 * -0x10000;
          }
          if ((iVar1 < iVar4) && (iVar1 < iVar2)) {
            param_1[uVar3 * 5 + 0x13] = iVar8 * 0x10000;
          }
        }
      }
    }
    if ((0 < iVar5) && (iVar2 = FT_DivFix(0x10000,iVar5), iVar2 < param_1[3])) {
      iVar2 = FT_DivFix(0x10000,iVar5);
      param_1[3] = iVar2;
    }
    if (*param_1 < param_1[3]) {
      *(undefined1 *)(param_1 + 2) = 1;
      iVar2 = FT_MulDiv(0x999a,*param_1,param_1[3]);
      param_1[6] = 0x999a - iVar2;
      if (0x7fff < param_1[6]) {
        param_1[6] = 0x7fff;
      }
    }
    if (*(char *)(param_2 + 0xba) != '\0') {
      param_1[6] = 0;
    }
    for (uVar3 = 0; uVar3 < (uint)param_1[1]; uVar3 = uVar3 + 1) {
      if ((char)param_1[uVar3 * 5 + 0x15] == '\0') {
        iVar2 = FT_MulFix(param_1[uVar3 * 5 + 0x13],*param_1);
        param_1[uVar3 * 5 + 0x14] = param_1[6] + iVar2 + 0x8000U & 0xffff0000;
      }
      else {
        iVar2 = FT_MulFix(param_1[uVar3 * 5 + 0x13],*param_1);
        param_1[uVar3 * 5 + 0x14] = (iVar2 - param_1[6]) + 0x8000U & 0xffff0000;
      }
    }
  }
  return;
}

