
void FUN_00439b54(int param_1)

{
  uint uVar1;
  
  uVar1 = *(uint *)(param_1 + 8);
  while (uVar1 < 0x10000) {
    FUN_0043996c(param_1 + 4,param_1 + 0x28);
    uVar1 = *(int *)(param_1 + 8) << 8;
    *(uint *)(param_1 + 8) = uVar1;
  }
  return;
}

