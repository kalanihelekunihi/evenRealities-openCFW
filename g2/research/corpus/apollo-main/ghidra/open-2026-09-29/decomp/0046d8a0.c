
undefined4 FUN_0046d8a0(int *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  
  if (((param_1 == (int *)0x0) || (param_2 == 0)) || (param_3 == 0)) {
    uVar1 = 0;
  }
  else {
    param_1[4] = 0;
    param_1[1] = param_3;
    *param_1 = param_2;
    param_1[3] = 0;
    param_1[2] = 0;
    uVar1 = 1;
  }
  return uVar1;
}

