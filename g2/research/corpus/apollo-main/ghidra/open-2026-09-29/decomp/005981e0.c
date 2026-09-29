
undefined8 FUN_005981e0(int *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00598134(param_1);
  if (iVar1 == 0) {
    *param_2 = *(undefined1 *)(*param_1 + param_1[2]);
    param_1[2] = param_1[2] + 1U & param_1[1];
  }
  return CONCAT44(param_4,(uint)(iVar1 == 0));
}

