
undefined4 FUN_00460090(int *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (int *)0x0) {
    uVar1 = 0xffffffff;
  }
  else if (*param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    *DAT_00460120 = (int)param_1;
    *DAT_0046011c = *param_1;
    uVar1 = 0;
  }
  return uVar1;
}

