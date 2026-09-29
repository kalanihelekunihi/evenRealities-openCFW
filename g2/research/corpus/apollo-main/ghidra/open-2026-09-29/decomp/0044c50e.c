
undefined4 FUN_0044c50e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = FUN_0044cd9e(param_1);
  if (*(int *)(param_1 + 8) == 0) {
    if ((uVar1 & 0xff) != 0) {
      FUN_0043e1fa(param_1);
      *(ushort *)(*(int *)(param_1 + 8) + 0x32) =
           *(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xf3ff | (ushort)((uVar1 & 3) << 10);
    }
  }
  else {
    *(ushort *)(*(int *)(param_1 + 8) + 0x32) =
         *(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xf3ff | (ushort)((uVar1 & 3) << 10);
  }
  return param_4;
}

