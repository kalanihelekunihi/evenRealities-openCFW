
int FUN_004caa88(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4,
                undefined4 param_5,int param_6,uint param_7,undefined4 *param_8)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined1 auStack_30 [8];
  undefined4 local_28;
  
  uVar4 = 0;
  local_28 = param_1;
  while( true ) {
    if (param_7 <= uVar4) {
      return 0;
    }
    iVar2 = lfs_min(param_7 - uVar4,8);
    iVar3 = FUN_004ca83c(local_28,param_2,param_3,param_4 - uVar4,param_5,uVar4 + param_6,auStack_30
                         ,iVar2);
    if (iVar3 != 0) break;
    uVar1 = FUN_00541af8(*param_8,auStack_30,iVar2);
    *param_8 = uVar1;
    uVar4 = iVar2 + uVar4;
  }
  return iVar3;
}

