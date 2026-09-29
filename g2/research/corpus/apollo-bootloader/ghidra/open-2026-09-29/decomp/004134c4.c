
/* WARNING: Type propagation algorithm not settling */

int FUN_004134c4(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5,
                code *param_6,undefined4 param_7)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int local_3c [5];
  int iStack_28;
  
  if (param_5 == 0) {
    iVar1 = 0;
  }
  else {
    local_3c[3] = param_5 + -1;
    iStack_28 = param_4;
    uVar2 = FUN_00413234(param_1,local_3c + 3);
    local_3c[4] = param_2;
    while (iVar1 = (*param_6)(param_7,param_4), iVar1 == 0) {
      if (uVar2 == 0) {
        return 0;
      }
      iVar4 = -(uVar2 & 1) + 2;
      local_3c[0] = iVar4 * 4;
      iVar1 = FUN_00410544(param_1,local_3c[4],param_3,iVar4 * 4,param_4,0,local_3c + 1);
      local_3c[1] = lfs_fromle32(local_3c[1]);
      local_3c[2] = lfs_fromle32(local_3c[2]);
      if (iVar1 != 0) {
        return iVar1;
      }
      for (iVar1 = 0; iVar1 < (int)(-(uVar2 & 1) + 1); iVar1 = iVar1 + 1) {
        iVar3 = (*param_6)(param_7,local_3c[iVar1 + 1]);
        if (iVar3 != 0) {
          return iVar3;
        }
      }
      param_4 = local_3c[iVar4];
      uVar2 = uVar2 - iVar4;
    }
  }
  return iVar1;
}

