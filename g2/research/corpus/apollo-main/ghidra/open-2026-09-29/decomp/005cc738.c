
void FUN_005cc738(undefined4 param_1,int param_2)

{
  *(undefined4 *)(param_2 + 0x2c) = 0xffffffff;
  *(byte *)(param_2 + 0x30) = *(byte *)(param_2 + 0x30) & 0xf8;
  FUN_0043dfa4(param_2,0x10);
  FUN_0043ded4(param_2,8);
  FUN_0043ded4(param_2,0x400);
  return;
}

