
int FUN_004cc23c(undefined4 param_1,int param_2,uint param_3,undefined4 *param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined1 auStack_28 [4];
  undefined4 local_24;
  undefined4 *puStack_20;
  
  puStack_20 = param_4;
  iVar1 = FUN_004caebe(param_3);
  if (*(uint *)(param_2 + 0x14) < (uint)(iVar1 + *(int *)(param_2 + 4))) {
    iVar2 = -0x1c;
  }
  else {
    local_24 = lfs_tobe32(param_3 & 0x7fffffff ^ *(uint *)(param_2 + 8));
    iVar2 = FUN_004cc200(param_1,param_2,&local_24,4);
    if (iVar2 == 0) {
      if ((int)param_3 < 0) {
        for (uVar3 = 0; uVar3 < iVar1 - 4U; uVar3 = uVar3 + 1) {
          iVar2 = FUN_004ca83c(param_1,0,param_1,(iVar1 + -4) - uVar3,*param_4,uVar3 + param_4[1],
                               auStack_28,1);
          if (iVar2 != 0) {
            return iVar2;
          }
          iVar2 = FUN_004cc200(param_1,param_2,auStack_28,1);
          if (iVar2 != 0) {
            return iVar2;
          }
        }
      }
      else {
        iVar1 = FUN_004cc200(param_1,param_2,param_4,iVar1 + -4);
        if (iVar1 != 0) {
          return iVar1;
        }
      }
      *(uint *)(param_2 + 8) = param_3 & 0x7fffffff;
      iVar2 = 0;
    }
  }
  return iVar2;
}

