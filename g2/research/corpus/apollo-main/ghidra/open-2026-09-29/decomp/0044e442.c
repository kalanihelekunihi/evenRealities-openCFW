
ushort FUN_0044e442(int param_1)

{
  ushort uVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    uVar1 = 0xf;
  }
  else {
    uVar1 = *(ushort *)(*(int *)(param_1 + 8) + 0x32) >> 6 & 0xf;
  }
  return uVar1;
}

