
undefined4 FUN_00598198(int *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00598146(param_1);
  if (iVar1 != 0) {
    param_1[2] = param_1[2] + 1U & param_1[1];
  }
  *(undefined1 *)(*param_1 + param_1[3]) = param_2;
  param_1[3] = param_1[3] + 1U & param_1[1];
  return param_4;
}

