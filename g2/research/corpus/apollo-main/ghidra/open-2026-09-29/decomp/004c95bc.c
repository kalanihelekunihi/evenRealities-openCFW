
undefined8 FUN_004c95bc(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = 1 << (param_2 & 0xff);
  uVar4 = param_2;
  osThreadFlagsSet(param_1,0x800000);
  uVar1 = osEventFlagsWait(*(undefined4 *)(DAT_004c9c58 + 0x1c),uVar3,1,20000,param_1,uVar4,param_3,
                           param_4);
  if ((uVar3 & uVar1) != uVar3) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xb1;
      uVar4 = DAT_004c9c98;
      FUN_0043d574(1,DAT_004c9ca4,DAT_004c9ca0,DAT_004c9c9c,0xb1,DAT_004c9c98,uVar1,param_2 & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      param_1 = param_2 & 0xff;
      compress_log_output(0x4800000,DAT_004c9ca8,DAT_004c9ca8,uVar1);
    }
  }
  return CONCAT44(uVar4,param_1);
}

