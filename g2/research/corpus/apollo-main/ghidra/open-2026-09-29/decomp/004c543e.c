
undefined8
Thread_SendEvtToRingTask
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0x176;
    param_2 = DAT_004c5704;
    param_3 = param_1;
    FUN_0043d574(4,DAT_004c5640,DAT_004c563c,DAT_004c5708,0x176,DAT_004c5704,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004c570c,DAT_004c570c,param_1,uVar2,param_2,param_3);
  }
  osThreadFlagsSet(*(undefined4 *)(DAT_004c5648 + 8),param_1);
  return CONCAT44(param_2,uVar2);
}

