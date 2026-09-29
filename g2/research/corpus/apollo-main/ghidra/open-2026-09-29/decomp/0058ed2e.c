
int FUN_0058ed2e(undefined4 *param_1,int *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_28;
  undefined4 uStack_24;
  
  local_28 = 0;
  if (param_1 == (undefined4 *)0x0) {
    local_28 = 0x21;
  }
  else if ((param_2 == (int *)0x0) || (param_3 == (int *)0x0)) {
    local_28 = 6;
  }
  else if (param_2 == param_3) {
    local_28 = 0;
  }
  else {
    if (param_2[2] < 0) {
      iVar2 = -1;
    }
    else {
      iVar2 = 1;
    }
    if (param_3[2] < 0) {
      iVar3 = -1;
    }
    else {
      iVar3 = 1;
    }
    uStack_24 = param_4;
    if (param_2[3] == 0) {
      FUN_00439c04(param_3,param_2,0x18);
      if (iVar2 != iVar3) {
        param_3[2] = -param_3[2];
      }
      local_28 = 0;
    }
    else {
      iVar4 = param_2[2];
      if (iVar4 < 0) {
        iVar4 = -iVar4;
      }
      iVar5 = *param_2 * iVar4;
      if (param_3[3] == 0) {
        iVar1 = ft_mem_qalloc(*param_1,iVar5,&local_28,param_4,param_1,param_2);
        param_3[3] = iVar1;
      }
      else {
        iVar1 = param_3[2];
        if (iVar1 < 0) {
          iVar1 = -iVar1;
        }
        if (*param_3 * iVar1 - iVar5 != 0) {
          iVar1 = ft_mem_qrealloc(*param_1,1,*param_3 * iVar1,iVar5,param_3[3],&local_28);
          param_3[3] = iVar1;
        }
      }
      if (local_28 == 0) {
        iVar1 = param_3[3];
        FUN_00439c04(param_3,param_2,0x18);
        param_3[3] = iVar1;
        if (iVar2 == iVar3) {
          FUN_00439be4(param_3[3],param_2[3],iVar5);
        }
        else {
          iVar3 = param_2[3];
          iVar5 = param_3[3] + (*param_3 + -1) * iVar4;
          for (iVar2 = *param_3; iVar2 != 0; iVar2 = iVar2 + -1) {
            FUN_00439be4(iVar5,iVar3,iVar4);
            iVar3 = iVar3 + iVar4;
            iVar5 = iVar5 - iVar4;
          }
        }
      }
    }
  }
  return local_28;
}

