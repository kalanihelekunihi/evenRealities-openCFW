
undefined8 thread_ble_wsf_wait_tx_ready(uint param_1,undefined4 param_2)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  
  iVar3 = osKernelGetTickCount();
  bVar6 = 0;
  cVar1 = threadBleWsfTakeTxReady(0);
  cVar2 = '\0';
  if (cVar1 == '\0') {
    do {
      if (cVar2 != '\0') goto LAB_004d0bde;
      cVar2 = threadBleWsfTakeTxReady(10);
      if (cVar2 == '\0') {
        osDelay(10);
      }
      bVar6 = bVar6 + 1;
    } while (bVar6 < 0x14);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0xd3;
      param_2 = DAT_004d0cfc;
      FUN_0043d574(2,PTR_s_task_ble_wsf_004d0cec,DAT_004d0ce8,DAT_004d0d00);
    }
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1f) {
      iVar4 = FUN_0043d0ce();
      if (-1 < iVar4 << 0x1d) goto LAB_004d0bde;
    }
    compress_log_output(0x8000000,DAT_004d0d04,DAT_004d0d04);
  }
LAB_004d0bde:
  iVar4 = osKernelGetTickCount();
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    param_1 = 0xd9;
    param_2 = DAT_004d0d08;
    FUN_0043d574(4,PTR_s_task_ble_wsf_004d0cec,DAT_004d0ce8,DAT_004d0d00,0xd9,DAT_004d0d08,
                 iVar4 - iVar3,bVar6);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    param_1 = (uint)bVar6;
    compress_log_output(0x10800000,DAT_004d0d0c,DAT_004d0d0c,iVar4 - iVar3);
  }
  return CONCAT44(param_2,param_1);
}

