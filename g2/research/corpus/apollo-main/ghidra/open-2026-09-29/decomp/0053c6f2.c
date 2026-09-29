
void AUD_CodecDmaInt(int param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = 0;
  local_14 = 0;
  iVar3 = *(int *)(param_1 + 8);
  iVar1 = osKernelGetTickCount();
  uVar2 = iVar1 - iVar3;
  if (uVar2 < 0x29) {
    gx8002_i2s_rx_buffer_get(&local_10,&local_14);
    *DAT_0053cedc = *DAT_0053cedc + 1;
    SVC_PcmAppProcessData(0,local_10,local_14);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,DAT_0053ced4,0x139,DAT_0053ced0,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0053ced8,DAT_0053ced8,uVar2);
    }
  }
  return;
}

