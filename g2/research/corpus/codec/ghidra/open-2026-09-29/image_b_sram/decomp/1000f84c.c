
/* WARNING: Removing unreachable block (ram,0x1000f96c) */
/* WARNING: Removing unreachable block (ram,0x1000fa4c) */
/* WARNING: Removing unreachable block (ram,0x1000f978) */

int FUN_1000f84c(int param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  undefined4 *puVar9;
  uint uVar10;
  undefined4 local_28;
  
  uVar10 = param_2 & 0x3fffffff;
  iVar2 = (int)param_2 >> 0x1f;
  if (DAT_1000faac < uVar10) {
    if ((param_2 & 0x7ffff) == 0 && param_1 == 0) {
      if ((int)param_2 < 0) {
        return 0;
      }
    }
    else {
      param_1 = FUN_10011de4(param_1,param_2,param_1,param_2);
    }
  }
  else {
    if (DAT_1000fab0 < uVar10) {
      if (DAT_1000fb04 < uVar10) {
        uVar10 = param_2;
        FUN_10011e50(param_1,param_2,DAT_1000faf0,DAT_1000faf4);
        FUN_10011de4();
        iVar2 = FUN_100122f8();
        uVar3 = FUN_10012290();
        uVar8 = uVar10;
        uVar4 = FUN_10011e50();
        uVar4 = FUN_10011e14(param_1,param_2,uVar4,uVar8);
        local_28 = FUN_10011e50(uVar3,uVar10,DAT_1000fafc,DAT_1000fb00);
      }
      else {
        iVar1 = iVar2 * -8;
        puVar9 = (undefined4 *)(PTR_DAT_1000fb08 + iVar1 + 0x10);
        uVar4 = FUN_10011e14(param_1,param_2,*(undefined4 *)(PTR_DAT_1000fb08 + iVar1),
                             *(undefined4 *)((int)(PTR_DAT_1000fb08 + iVar1) + 4));
        uVar10 = puVar9[1];
        local_28 = *puVar9;
        iVar2 = iVar2 * 2 + 1;
      }
      param_1 = FUN_10011e14(uVar4,param_2,local_28,uVar10);
    }
    else {
      FUN_10011de4(param_1,param_2,DAT_1000fb0c,DAT_1000fb10);
      iVar2 = FUN_100121a0();
      if (0 < iVar2) {
        iVar2 = FUN_10011de4(param_1,param_2,0,0);
        return iVar2;
      }
      iVar2 = 0;
      local_28 = 0;
      uVar10 = 0;
    }
    uVar8 = param_2;
    FUN_10011e50(param_1,param_2,param_1,param_2);
    FUN_10011e50();
    FUN_10011e14();
    FUN_10011e50();
    FUN_10011de4();
    FUN_10011e50();
    FUN_10011e14();
    FUN_10011e50();
    FUN_10011de4();
    uVar3 = FUN_10011e50();
    uVar5 = param_2;
    uVar3 = FUN_10011e14(param_1,param_2,uVar3,uVar8);
    if (iVar2 == 0) {
      uVar4 = FUN_10011e50(param_1,param_2,uVar3,uVar5);
      uVar3 = FUN_10011e14(uVar3,uVar5,0,0);
      FUN_10012050(uVar4,param_2,uVar3,uVar5);
      uVar3 = FUN_10011e14();
      iVar2 = FUN_10011e14(0,0,uVar3,param_2);
      return iVar2;
    }
    uVar4 = FUN_10011e50(param_1,param_2,uVar3,uVar5);
    uVar6 = 0;
    uVar3 = FUN_10011e14(0,0,uVar3,uVar5);
    uVar3 = FUN_10012050(uVar4,param_2,uVar3,uVar6);
    FUN_10011e14(local_28,uVar10,uVar3,param_2);
    uVar3 = FUN_10011e14();
    iVar7 = 0;
    iVar1 = FUN_10011e14(0,0,uVar3,uVar10);
    if (-0x3fe < iVar2) {
      return iVar1;
    }
    param_1 = FUN_10011e50(iVar1,iVar7 + (iVar2 + 1000) * 0x100000,0,0);
  }
  return param_1;
}

