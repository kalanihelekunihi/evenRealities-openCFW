
undefined4 FUN_0044e3ca(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_0043e1fa(param_1);
  if ((param_2 & 0xff) != (*(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0x3ff) >> 6) {
    *(ushort *)(*(int *)(param_1 + 8) + 0x32) =
         *(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xfc3f | (ushort)((param_2 & 0xf) << 6);
  }
  return param_4;
}

