
longlong FUN_005894d6(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar1 = FUN_0044dca2(param_1);
  iVar2 = FUN_0044ddea(uVar1);
  uVar3 = FUN_0044de92(param_1);
  iVar4 = FUN_0044e498(uVar1);
  iVar5 = FUN_0043fdda(param_1);
  iVar6 = FUN_0043fdda(uVar1);
  uVar7 = uVar3 - iVar4 / iVar5;
  if ((int)uVar7 < 2) {
    if (uVar3 == 0) {
      FUN_0044ea2e(param_1,1);
    }
    else {
      uVar1 = FUN_0044dce2(uVar1,uVar3 - 1);
      FUN_0044ea2e(uVar1,1);
    }
  }
  else if (uVar7 < iVar6 / iVar5 - 2U) {
    FUN_0044ea2e(param_1,1);
  }
  else if (uVar3 < iVar2 - 1U) {
    uVar1 = FUN_0044dce2(uVar1,uVar3 + 1);
    FUN_0044ea2e(uVar1,1);
  }
  else {
    FUN_0044ea2e(param_1,1);
  }
  return (ulonglong)param_4 << 0x20;
}

