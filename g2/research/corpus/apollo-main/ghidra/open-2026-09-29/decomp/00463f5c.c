
undefined4 FUN_00463f5c(int *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((param_1 != (int *)0x0) && (param_2 < (uint)param_1[2])) {
    iVar1 = osKernelGetTickCount();
    param_1[5] = iVar1;
    param_1[3] = param_2;
    if ((param_1[1] != 0) &&
       (((*(int *)(param_1[1] + param_2 * 4) != 0 && (*param_1 != 0)) &&
        (iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0)))) {
      FUN_00498680(*param_1,*(undefined4 *)(param_1[1] + param_2 * 4));
    }
  }
  return param_4;
}

