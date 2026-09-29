
undefined4 FUN_00482d88(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 1;
  }
  else if ((*(int *)(param_1 + 4) == 0) && (*(int *)(param_1 + 8) == 0)) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

