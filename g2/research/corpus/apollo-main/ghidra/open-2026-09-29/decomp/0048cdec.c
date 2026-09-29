
undefined4 FUN_0048cdec(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  
  iVar2 = FUN_0048c986(param_1);
  bVar1 = false;
  if (iVar2 == 0) {
    FUN_0044dca2(param_1);
    iVar3 = FUN_0048c986();
    uVar6 = DAT_0048d3c0;
    if (iVar3 == 0) {
      FUN_0044d25c(2,DAT_0048d3b0,0x179,DAT_0048d3c4);
      return uVar6;
    }
    iVar4 = FUN_0048c99a(param_1);
    iVar5 = FUN_0048c9ae(param_1);
    iVar2 = FUN_0044f718((iVar5 + 1) * 4);
    FUN_00454738(iVar2,iVar3 + iVar4 * 4,iVar5 << 2);
    *(undefined4 *)(iVar2 + iVar5 * 4) = 0x1fffffff;
    bVar1 = true;
  }
  uVar6 = FUN_0048d4d0(iVar2);
  *(undefined4 *)(param_2 + 0x14) = uVar6;
  uVar6 = FUN_0044f718(*(int *)(param_2 + 0x14) << 2);
  *(undefined4 *)(param_2 + 4) = uVar6;
  uVar6 = FUN_0044f718(*(int *)(param_2 + 0x14) << 2);
  *(undefined4 *)(param_2 + 0xc) = uVar6;
  for (uVar9 = 0; uVar9 < *(uint *)(param_2 + 0x14); uVar9 = uVar9 + 1) {
    if (*(int *)(iVar2 + uVar9 * 4) == DAT_0048d3b8) {
      iVar3 = DAT_0048d3b4;
      for (uVar10 = 0; uVar7 = FUN_0044ddea(param_1), uVar10 < uVar7; uVar10 = uVar10 + 1) {
        uVar6 = FUN_0044dce2(param_1,uVar10);
        iVar4 = FUN_0043e11c(uVar6,DAT_0048d3bc);
        if ((((iVar4 == 0) && (iVar4 = FUN_0048c9ae(uVar6), iVar4 == 1)) &&
            (uVar7 = FUN_0048c99a(uVar6), uVar7 == uVar9)) &&
           (iVar4 = FUN_0043fdda(uVar6), iVar3 <= iVar4)) {
          iVar3 = FUN_0043fdda(uVar6);
        }
      }
      if (iVar3 < 0) {
        *(undefined4 *)(*(int *)(param_2 + 0xc) + uVar9 * 4) = 0;
      }
      else {
        *(int *)(*(int *)(param_2 + 0xc) + uVar9 * 4) = iVar3;
      }
    }
  }
  iVar3 = 0;
  iVar4 = 0;
  for (uVar9 = 0; uVar9 < *(uint *)(param_2 + 0x14); uVar9 = uVar9 + 1) {
    iVar5 = *(int *)(iVar2 + uVar9 * 4);
    if (iVar5 < DAT_0048d3a4) {
      if (iVar5 == DAT_0048d3b8) {
        iVar4 = *(int *)(*(int *)(param_2 + 0xc) + uVar9 * 4) + iVar4;
      }
      else {
        *(int *)(*(int *)(param_2 + 0xc) + uVar9 * 4) = iVar5;
        iVar4 = iVar5 + iVar4;
      }
    }
    else {
      iVar3 = iVar5 + -0x1fffff9b + iVar3;
    }
  }
  iVar5 = FUN_0048c856(param_1,0);
  iVar8 = FUN_0043fe70(param_1);
  iVar4 = (iVar8 - (*(int *)(param_2 + 0x14) + -1) * iVar5) - iVar4;
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  uVar9 = 0;
  while ((uVar9 < *(uint *)(param_2 + 0x14) && (iVar3 != 0))) {
    iVar5 = *(int *)(iVar2 + uVar9 * 4);
    if (DAT_0048d3a4 <= iVar5) {
      iVar5 = iVar5 + -0x1fffff9b;
      uVar6 = FUN_0048ca18(iVar5 * iVar4,iVar3);
      *(undefined4 *)(*(int *)(param_2 + 0xc) + uVar9 * 4) = uVar6;
      iVar3 = iVar3 - iVar5;
      iVar4 = iVar4 - *(int *)(*(int *)(param_2 + 0xc) + uVar9 * 4);
    }
    uVar9 = uVar9 + 1;
  }
  if (bVar1) {
    FUN_0044f758(iVar2);
  }
  return param_4;
}

