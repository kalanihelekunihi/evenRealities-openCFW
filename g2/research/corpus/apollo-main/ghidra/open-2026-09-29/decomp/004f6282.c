
undefined8 FUN_004f6282(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = param_1;
  iVar2 = FUN_004f61f4();
  if (iVar2 != 0) {
    uVar3 = osKernelGetTickCount();
    puVar1 = DAT_004f6a00;
    *DAT_004f6a00 = uVar3;
    puVar1[1] = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar4 = 0x4b6;
      param_2 = DAT_004f6a0c;
      FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f6d28,0x4b6,DAT_004f6a0c,param_1 & 0xff,
                   param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004f6d60,DAT_004f6d60,param_1 & 0xff);
    }
    FUN_004f5fd0(param_1 & 0xff);
  }
  return CONCAT44(param_2,uVar4);
}

