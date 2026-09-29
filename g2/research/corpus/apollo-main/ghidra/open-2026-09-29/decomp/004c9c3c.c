
undefined4 FUN_004c9c3c(uint param_1)

{
  undefined4 unaff_r7;
  
  osEventFlagsSet(*(undefined4 *)(DAT_004c9c58 + 0x1c),1 << (param_1 & 0xff));
  return unaff_r7;
}

