
void FUN_00557e34(undefined4 param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  cVar1 = FUN_004516f8(DAT_00557fec,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    iVar3 = *param_2;
    if (iVar2 == 0x1b) {
      iVar2 = FUN_00452c66(iVar3,0x20000);
      piVar4 = (int *)param_2[4];
      if (iVar2 < *piVar4) {
        iVar2 = *piVar4;
      }
      *piVar4 = iVar2;
      iVar5 = FUN_005574ea(iVar3,0);
      iVar6 = FUN_005574f4(iVar3,0);
      iVar7 = FUN_005574d6(iVar3,0);
      iVar3 = FUN_005574e0(iVar3,0);
      iVar2 = iVar6;
      if (iVar5 < iVar6) {
        iVar2 = iVar5;
      }
      iVar8 = iVar3;
      if (iVar7 < iVar3) {
        iVar8 = iVar7;
      }
      if (iVar2 < iVar8) {
        iVar3 = iVar5;
        if (iVar6 <= iVar5) {
          iVar3 = iVar6;
        }
      }
      else if (iVar7 < iVar3) {
        iVar3 = iVar7;
      }
      if (iVar3 < 0) {
        *piVar4 = *piVar4 - iVar3;
      }
    }
    else if ((iVar2 == 1) || (iVar2 == 0xb)) {
      FUN_004405d4(iVar3,iVar3 + 0x3c);
    }
    else if (iVar2 == 0x1d) {
      FUN_00557890(param_2);
    }
  }
  return;
}

