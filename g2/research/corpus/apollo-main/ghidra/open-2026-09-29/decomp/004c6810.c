
void device_mgr_fn_004c6810(void)

{
  ushort *puVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  
  pcVar2 = (char *)FUN_0050938e(0);
  if (*pcVar2 != '\x01') {
    if (*pcVar2 == '\x02') {
      DRV_Bq25180RefreshStatus();
      bq27427_init_wrapper();
    }
    goto LAB_004c688e;
  }
  iVar3 = FUN_00510fe2(DAT_004c6cb0);
  if (iVar3 != DAT_004c6cb4) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,DAT_004c6cbc,0x195,DAT_004c6cb8,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1f) {
      iVar4 = FUN_0043d0ce();
      if (-1 < iVar4 << 0x1d) goto LAB_004c687a;
    }
    compress_log_output(0x4400000,DAT_004c6cc0,DAT_004c6cc0,iVar3);
  }
LAB_004c687a:
  FUN_005128a0();
LAB_004c688e:
  iVar3 = productModeGet();
  if (iVar3 != 1) {
    CHG_OnBatteryLevelChanged();
  }
  puVar1 = DAT_004c6cc4;
  *DAT_004c6cc4 = *DAT_004c6cc4 + 1;
  if (9 < *puVar1) {
    *puVar1 = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004c6c00,DAT_004c6bfc,DAT_004c6cbc,0x1ab,DAT_004c6cc8,
                   *(undefined4 *)(DAT_004c6ca0 + 4),*(undefined4 *)(DAT_004c6ca0 + 8),
                   *(undefined4 *)(DAT_004c6ca0 + 0xc),*(undefined4 *)(DAT_004c6ca0 + 0x10));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xd000000,DAT_004c6ccc,DAT_004c6ccc,*(undefined4 *)(DAT_004c6ca0 + 4),
                          *(undefined4 *)(DAT_004c6ca0 + 8),*(undefined4 *)(DAT_004c6ca0 + 0xc),
                          *(undefined4 *)(DAT_004c6ca0 + 0x10));
    }
  }
  return;
}

