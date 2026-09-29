
undefined4 * FUN_005d916e(undefined4 *param_1,uint param_2,int param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 *local_18;
  
  local_18 = param_4;
  if (param_1[1] == 0) {
    if (1 < param_2) {
      param_2 = (uint)(param_2 != 0);
    }
    for (; 0 < param_3; param_3 = param_3 + -1) {
      local_18 = (undefined4 *)0x0;
      iVar1 = FUN_005d8fae(param_1 + param_2 * 9 + 4,*param_4,param_4[1],*param_1);
      if (iVar1 != 0) {
        param_1[1] = iVar1;
        return (undefined4 *)0x0;
      }
      param_4 = param_4 + 2;
    }
  }
  return local_18;
}

