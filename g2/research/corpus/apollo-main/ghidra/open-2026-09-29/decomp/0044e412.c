
undefined4 FUN_0044e412(int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_0043e1fa(param_1);
  *(ushort *)(*(int *)(param_1 + 8) + 0x32) =
       *(ushort *)(*(int *)(param_1 + 8) + 0x32) & 0xffcf | (param_2 & 3) << 4;
  return param_4;
}

