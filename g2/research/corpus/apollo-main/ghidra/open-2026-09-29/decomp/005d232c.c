
undefined4 FUN_005d232c(undefined4 *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int local_18;
  undefined4 uStack_14;
  
  local_18 = 0;
  iVar2 = param_1[2];
  uStack_14 = param_4;
  if (param_2 <= 0x7fffffff / (uint)param_1[2]) {
    uVar1 = ft_mem_realloc(*param_1,1,param_1[6],iVar2 * param_2,param_1[7],&local_18);
    param_1[7] = uVar1;
    if (local_18 == 0) {
      param_1[3] = param_2;
      param_1[6] = iVar2 * param_2;
      if (param_2 < (uint)param_1[5]) {
        FUN_005d2a0a(param_1[1],0x82);
        param_1[5] = param_2;
        return 0;
      }
      return 1;
    }
  }
  FUN_005d2a0a(param_1[1],0x40);
  return 0;
}

