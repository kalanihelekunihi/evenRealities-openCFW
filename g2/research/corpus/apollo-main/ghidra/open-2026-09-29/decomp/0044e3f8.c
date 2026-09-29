
undefined4 FUN_0044e3f8(int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_0043e1fa(param_1);
  *(ushort *)(*(int *)(param_1 + 8) + 0x32) =
       *(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xfff3 | (param_2 & 3) << 2;
  return param_4;
}

