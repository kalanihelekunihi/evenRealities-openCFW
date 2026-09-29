
undefined4 FUN_005d3a2a(int param_1,int param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  
  bVar1 = true;
  iVar2 = FUN_005d3644(param_2);
  if (iVar2 == 0) {
    bVar1 = false;
    iVar2 = param_3;
  }
  else {
    iVar3 = FUN_005d3644(param_3);
    iVar2 = param_2;
    if (iVar3 == 0) {
      bVar1 = false;
    }
  }
  if ((!bVar1) || (*(int *)(param_2 + 8) <= *(int *)(param_3 + 8))) {
    uVar6 = 0;
    while ((uVar6 < *(uint *)(param_1 + 0x14) &&
           (*(int *)(uVar6 * 0x14 + param_1 + 0x24) < *(int *)(iVar2 + 8)))) {
      uVar6 = uVar6 + 1;
    }
    if ((*(uint *)(param_1 + 0x14) <= uVar6) ||
       ((*(int *)(uVar6 * 0x14 + param_1 + 0x24) != *(int *)(iVar2 + 8) &&
        (((!bVar1 || (*(int *)(param_3 + 8) < *(int *)(uVar6 * 0x14 + param_1 + 0x24))) &&
         (iVar3 = FUN_005d3666(uVar6 * 0x14 + param_1 + 0x1c), iVar3 == 0)))))) {
      iVar3 = FUN_005d36ea(*(undefined4 *)(param_1 + 4));
      if ((iVar3 != 0) && (iVar3 = FUN_005d3696(iVar2), iVar3 == 0)) {
        if (bVar1) {
          iVar3 = FUN_005d36f0(*(undefined4 *)(param_1 + 4),
                               (*(int *)(iVar2 + 8) + *(int *)(param_3 + 8)) / 2);
          iVar4 = FT_MulFix((*(int *)(param_3 + 8) - *(int *)(iVar2 + 8)) / 2,
                            *(undefined4 *)(param_1 + 0x10));
          *(int *)(iVar2 + 0xc) = iVar3 - iVar4;
          *(int *)(param_3 + 0xc) = iVar4 + iVar3;
        }
        else {
          uVar5 = FUN_005d36f0(*(undefined4 *)(param_1 + 4),*(undefined4 *)(iVar2 + 8));
          *(undefined4 *)(iVar2 + 0xc) = uVar5;
        }
      }
      if ((uVar6 == 0) || (*(int *)(uVar6 * 0x14 + param_1 + 0x14) <= *(int *)(iVar2 + 0xc))) {
        if (uVar6 < *(uint *)(param_1 + 0x14)) {
          if (bVar1) {
            if (*(int *)(uVar6 * 0x14 + param_1 + 0x28) < *(int *)(param_3 + 0xc)) {
              return param_4;
            }
          }
          else if (*(int *)(uVar6 * 0x14 + param_1 + 0x28) < *(int *)(iVar2 + 0xc)) {
            return param_4;
          }
        }
        iVar3 = *(int *)(param_1 + 0x14);
        if (bVar1) {
          uVar7 = *(int *)(param_1 + 0x14) + 1;
        }
        else {
          uVar7 = *(uint *)(param_1 + 0x14);
        }
        iVar4 = *(int *)(param_1 + 0x14) - uVar6;
        if (uVar7 < 0xc0) {
          while( true ) {
            iVar3 = iVar3 + -1;
            if (iVar4 == 0) break;
            FUN_00439c04(uVar7 * 0x14 + param_1 + 0x1c,iVar3 * 0x14 + param_1 + 0x1c,0x14);
            uVar7 = uVar7 - 1;
            iVar4 = iVar4 + -1;
          }
          FUN_00439c04(uVar6 * 0x14 + param_1 + 0x1c,iVar2,0x14);
          *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x14) + 1;
          if (bVar1) {
            FUN_00439c04(param_1 + uVar6 * 0x14 + 0x30,param_3,0x14);
            *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x14) + 1;
          }
        }
      }
    }
  }
  return param_4;
}

