
undefined8 _ancsValueUpdate(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  piVar1 = DAT_004bf8f0;
  local_18 = param_3;
  local_14 = param_4;
  if (((((*(short *)(param_1 + 10) == *(short *)*DAT_004bf8f0) ||
        (*(short *)(param_1 + 10) == *(short *)(*DAT_004bf8f0 + 6))) ||
       (*(short *)(param_1 + 10) == *(short *)(*DAT_004bf8f0 + 4))) &&
      ((iVar2 = service_ancc_state_byte0_get(), iVar2 == 1 &&
       (iVar2 = semantic_OtaTransferActive(), iVar2 == 0)))) &&
     (iVar2 = semantic_EfsTransferActive(), iVar2 == 0)) {
    iVar2 = osKernelGetTickCount();
    iVar3 = FUN_004b8204();
    if ((uint)(iVar2 - iVar3) < 5000) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = DAT_004bf8f4;
        local_18 = 0x1d4;
        FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf8f8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bf8fc,DAT_004bf8fc);
      }
    }
    else {
      _anccNtfValueUpdate(*piVar1,param_1);
    }
  }
  return CONCAT44(local_14,local_18);
}

