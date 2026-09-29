
undefined4 FUN_00557802(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  *(undefined4 *)(param_2 + 0x30) = 0;
  *(undefined4 *)(param_2 + 0x34) = 100;
  *(undefined4 *)(param_2 + 0x38) = 0;
  *(undefined4 *)(param_2 + 0x2c) = 0;
  *(undefined4 *)(param_2 + 0x3c) = 0;
  *(undefined4 *)(param_2 + 0x44) = 0;
  *(undefined4 *)(param_2 + 0x40) = 0;
  *(undefined4 *)(param_2 + 0x48) = 0;
  *(byte *)(param_2 + 0x70) = *(byte *)(param_2 + 0x70) & 0xf8;
  *(byte *)(param_2 + 0x70) = *(byte *)(param_2 + 0x70) & 199;
  *(undefined1 *)(param_2 + 0x4c) = 0;
  FUN_0055801c(param_2,param_2 + 0x50);
  FUN_0055801c(param_2,param_2 + 0x60);
  FUN_0043dfa4(param_2,8);
  FUN_0043dfa4(param_2,0x10);
  FUN_00557536(param_2,0,0);
  return param_4;
}

