
undefined4 FUN_00557f1c(int *param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  param_1 = (int *)*param_1;
  iVar1 = *param_1;
  param_1[3] = -1;
  if (param_1 == (int *)(iVar1 + 0x50)) {
    *(int *)(iVar1 + 0x2c) = param_1[2];
  }
  else if (param_1 == (int *)(iVar1 + 0x60)) {
    *(int *)(iVar1 + 0x38) = param_1[2];
  }
  FUN_00440656(*param_1);
  return unaff_r7;
}

