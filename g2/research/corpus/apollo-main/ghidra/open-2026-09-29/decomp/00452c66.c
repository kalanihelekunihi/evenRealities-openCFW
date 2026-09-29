
int FUN_00452c66(undefined4 param_1,undefined4 param_2)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar8 = 0;
  iVar2 = FUN_00452450(param_1,param_2);
  if ((iVar2 != 0) && (bVar1 = FUN_00452498(param_1,param_2), 2 < bVar1)) {
    iVar3 = FUN_0045246e(param_1,param_2);
    iVar4 = FUN_0045245a(param_1,param_2);
    iVar5 = FUN_00452464(param_1,param_2);
    iVar6 = iVar5;
    if (iVar5 < 1) {
      iVar6 = -iVar5;
    }
    iVar7 = iVar4;
    if (iVar4 < 1) {
      iVar7 = -iVar4;
    }
    if (iVar6 < iVar7) {
      iVar5 = iVar4;
      if (iVar4 < 1) {
        iVar5 = -iVar4;
      }
    }
    else if (iVar5 < 1) {
      iVar5 = -iVar5;
    }
    iVar5 = iVar5 + iVar3 + iVar2 / 2 + 1;
    if (-1 < iVar5) {
      iVar8 = iVar5;
    }
  }
  iVar2 = FUN_00452410(param_1,param_2);
  if (((iVar2 != 0) && (bVar1 = FUN_0045243a(param_1,param_2), 2 < bVar1)) &&
     (iVar5 = FUN_00452446(param_1,param_2), iVar8 <= iVar2 + iVar5)) {
    iVar8 = iVar2 + iVar5;
  }
  iVar2 = FUN_004522d4(param_1,param_2);
  iVar5 = FUN_004522de(param_1,param_2);
  if (iVar2 <= iVar5) {
    iVar2 = iVar5;
  }
  if (0 < iVar2) {
    iVar8 = iVar2 + iVar8;
  }
  return iVar8;
}

