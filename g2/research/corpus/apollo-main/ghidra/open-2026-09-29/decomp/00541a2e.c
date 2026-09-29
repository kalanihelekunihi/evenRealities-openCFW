
undefined8
uart_instance_init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_00541ae0;
  iVar2 = osThreadNew(DAT_00541ae8,0,DAT_00541ae4,param_4,param_3,param_4);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0xc5;
      FUN_0043d574(1,DAT_00541aa4,DAT_00541aa0,DAT_00541af0,0xc5,DAT_00541aec);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00541af4);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = 0;
  }
  return CONCAT44(param_3,uVar3);
}

