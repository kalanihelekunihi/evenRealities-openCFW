
undefined4
DRV_Bq25180HwInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0053af78,DAT_0053af60,DAT_0053afa8,0x1e4,DAT_0053afa4,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0053aeba;
  }
  compress_log_output(0x10000000,DAT_0053afac,DAT_0053afac);
LAB_0053aeba:
  iVar1 = bq25180_read_device_id();
  if (iVar1 == 0) {
    bq25180_apply_defaults();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053af78,DAT_0053af60,DAT_0053afa8,0x1ef,DAT_0053afb8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053afbc,DAT_0053afbc);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053af78,DAT_0053af60,DAT_0053afa8,0x1e9,DAT_0053afb0,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0053afb4,DAT_0053afb4,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

