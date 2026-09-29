
undefined4 FUN_00452dc8(int param_1)

{
  undefined4 uVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = *(undefined4 *)(*(int *)(param_1 + 8) + 0x2c);
  }
  return uVar1;
}

