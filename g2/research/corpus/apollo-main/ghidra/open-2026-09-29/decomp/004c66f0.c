
undefined8 device_mgr_fn_004c66f0(int param_1)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if ((param_1 == 0) || (*(ushort *)(param_1 + 2) < 2)) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s__DEV_RingBatteryReportProcess__i_004c6c94;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x151;
      FUN_0043d574(2,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_RingBatteryReportProcess_004c6c98);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__device_mgr__DEV_RingBatteryRepo_004c6c9c,
                          PTR_s__device_mgr__DEV_RingBatteryRepo_004c6c9c);
    }
  }
  else {
    SVC_RingBattery_Update(*(undefined1 *)(param_1 + 4),*(undefined1 *)(param_1 + 5));
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

