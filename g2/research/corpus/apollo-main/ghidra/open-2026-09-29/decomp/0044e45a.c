
uint FUN_0044e45a(int param_1)

{
  uint uVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (*(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xf) >> 2;
  }
  return uVar1;
}

