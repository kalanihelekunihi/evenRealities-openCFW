
void FUN_005c7212(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int local_2c;
  int local_28;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  cVar1 = FUN_004516f8(DAT_005c7324,param_2);
  if (cVar1 == '\x01') {
    iVar2 = FUN_00450286(param_2);
    iVar3 = *param_2;
    if (iVar2 == 0x34) {
      piVar4 = (int *)param_2[4];
      iVar2 = FUN_005c719a(iVar3,0);
      iVar5 = *(int *)(iVar2 + 0xc);
      uVar6 = FUN_005c71ae(iVar3,0);
      uVar7 = FUN_005c71a4(iVar3,0);
      FUN_00489546(&local_2c,*(undefined4 *)(iVar3 + 0x2c),iVar2,uVar7,uVar6,0x1fffffff,0);
      iVar2 = FUN_005c7186(iVar3,0);
      iVar8 = FUN_005c7172(iVar3,0x20000);
      iVar9 = FUN_005c717c(iVar3,0x20000);
      iVar10 = FUN_005c715e(iVar3,0x20000);
      iVar3 = FUN_005c7168(iVar3,0x20000);
      iVar3 = iVar3 + iVar10 + iVar5;
      *piVar4 = iVar2 + local_2c + iVar9 + iVar8 + iVar5;
      if (local_28 < iVar3) {
        local_28 = iVar3;
      }
      piVar4[1] = local_28;
    }
    else if (iVar2 == 0x1b) {
      piVar4 = (int *)param_2[4];
      iVar2 = FUN_00452c66(iVar3,0x20000);
      if (iVar2 < *piVar4) {
        iVar2 = *piVar4;
      }
      *piVar4 = iVar2;
    }
    else if (iVar2 == 0x1d) {
      FUN_005c732c(param_2);
    }
  }
  return;
}

