
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0058c7a0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_00597e90();
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      FUN_00597ea6(iVar1,_DAT_0058c820,6);
      FUN_00597f10(iVar1,600);
      FUN_00597f52(iVar1,100);
      iVar2 = FUN_00597f82(iVar1);
      if (iVar2 != 0) {
        *(undefined4 *)(iVar2 + 0x40) = 400;
        if (param_2 != 0) {
          *(int *)(iVar2 + 0x10) = param_2;
        }
      }
      uVar3 = FUN_0044104c(0);
      FUN_0044127e(iVar1,uVar3,0);
      FUN_0044129e(iVar1,0xff,0);
      FUN_0058c824(iVar1);
    }
  }
  return iVar1;
}

