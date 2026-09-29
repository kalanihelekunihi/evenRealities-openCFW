
ulonglong FUN_004c96b6(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c94 + 8),0x800000);
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c80 + 8),0x800000);
  uVar1 = 0x842;
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c84 + 8),0x800000);
  if (-1 < param_1 << 0x1a) {
    osThreadFlagsSet(*(undefined4 *)(DAT_004c9c88 + 8),0x800000);
    osThreadFlagsSet(*(undefined4 *)(DAT_004c9c8c + 8),0x800000);
    uVar1 = 0xbc2;
    osThreadFlagsSet(*(undefined4 *)(DAT_004c9c90 + 8),0x800000);
  }
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c70 + 8),0x800000);
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c74 + 8),0x800000);
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9c78 + 8),0x800000);
  osThreadFlagsSet(*(undefined4 *)(DAT_004c9cac + 8),0x800000);
  return CONCAT44(param_4,uVar1) | 0x1038;
}

