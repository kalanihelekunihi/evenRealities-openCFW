
int FUN_0041070c(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4,
                undefined4 param_5,int param_6,int param_7,uint param_8)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined1 auStack_2c [8];
  
  uVar3 = 0;
  while( true ) {
    if (param_8 <= uVar3) {
      return 0;
    }
    iVar1 = lfs_min(param_8 - uVar3,8);
    iVar2 = FUN_00410544(param_1,param_2,param_3,param_4 - uVar3,param_5,uVar3 + param_6,auStack_2c,
                         iVar1);
    if (iVar2 != 0) break;
    iVar2 = FUN_00415758(auStack_2c,param_7 + uVar3,iVar1);
    if (iVar2 != 0) {
      if (iVar2 < 0) {
        return 1;
      }
      return 2;
    }
    uVar3 = iVar1 + uVar3;
  }
  return iVar2;
}

