
undefined4 FUN_0044d5f8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  
  bVar1 = *(byte *)(param_1 + 0x1c);
  *(byte *)(param_1 + 0x1c) = *(byte *)(param_1 + 0x1c) | 8;
  if ((*(byte *)(param_1 + 0x1c) & 7) >> 2 == 0) {
    FUN_0044d45c(param_1);
  }
  else if ((*(byte *)(param_1 + 0x1c) & 7) >> 2 != 0) {
    FUN_0044d4b6(param_1);
  }
  *(byte *)(param_1 + 0x1c) = *(byte *)(param_1 + 0x1c) & 0xf7 | bVar1 & 8;
  return param_4;
}

