
undefined8 FUN_004c9be2(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar2 = 0x1bf;
    param_2 = DAT_004c9d38;
    FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,DAT_004c9d3c,0x1bf,DAT_004c9d38,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004c9d40,DAT_004c9d40,param_1 & 0xff,uVar2,param_2,param_3);
  }
  osEventFlagsSet(*(undefined4 *)(DAT_004c9c58 + 0x1c),1 << (param_1 & 0xff));
  return CONCAT44(param_2,uVar2);
}

