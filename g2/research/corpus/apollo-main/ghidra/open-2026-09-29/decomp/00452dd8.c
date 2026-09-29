
ushort FUN_00452dd8(int param_1)

{
  ushort uVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = *(ushort *)(*(int *)(param_1 + 8) + 0x32) >> 10 & 3;
  }
  return uVar1;
}

