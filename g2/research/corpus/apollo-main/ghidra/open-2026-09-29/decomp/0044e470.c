
uint FUN_0044e470(int param_1)

{
  uint uVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (*(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0x3f) >> 4;
  }
  return uVar1;
}

