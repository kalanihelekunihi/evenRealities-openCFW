
void FUN_005cc778(undefined4 param_1,undefined4 *param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  
  cVar1 = FUN_004516f8(PTR_PTR_005ccb04,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    uVar3 = *param_2;
    if (iVar2 == 0x1b) {
      iVar4 = FUN_005cc70e(uVar3,0x30000);
      iVar5 = FUN_005cc718(uVar3,0x30000);
      iVar6 = FUN_005cc6fa(uVar3,0x30000);
      iVar7 = FUN_005cc704(uVar3,0x30000);
      iVar2 = iVar6;
      if (iVar6 < iVar7) {
        iVar2 = iVar7;
      }
      iVar9 = iVar5;
      if (iVar5 < iVar4) {
        iVar9 = iVar4;
      }
      if (iVar2 < iVar9) {
        iVar6 = iVar4;
        if (iVar4 <= iVar5) {
          iVar6 = iVar5;
        }
      }
      else if (iVar6 < iVar7) {
        iVar6 = iVar7;
      }
      iVar2 = FUN_00452c66(uVar3,0x30000);
      iVar2 = iVar2 + iVar6 + 2;
      piVar8 = (int *)param_2[4];
      if (iVar2 < *piVar8) {
        iVar2 = *piVar8;
      }
      *piVar8 = iVar2;
      iVar2 = FUN_00452c66(uVar3,0x20000);
      if (iVar2 < *piVar8) {
        iVar2 = *piVar8;
      }
      else {
        iVar2 = FUN_00452c66(uVar3,0x20000);
      }
      *piVar8 = iVar2;
    }
    else if (iVar2 == 0x23) {
      FUN_005cca4a(uVar3);
      FUN_00440656(uVar3);
    }
    else if (iVar2 == 0x1d) {
      FUN_005cc85e(param_2);
    }
  }
  return;
}

