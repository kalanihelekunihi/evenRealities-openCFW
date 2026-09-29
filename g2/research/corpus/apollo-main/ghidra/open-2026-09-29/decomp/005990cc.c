
void FUN_005990cc(int param_1,int param_2,int param_3)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 0x20);
  param_3 = param_3 + uVar1;
  if (param_3 < 0x21) {
    *(int *)(param_1 + 0x20) = param_3;
    *(uint *)(param_1 + 0x1c) = param_2 << (uVar1 & 0xff) | *(uint *)(param_1 + 0x1c);
    return;
  }
  FUN_00439b12();
  return;
}

