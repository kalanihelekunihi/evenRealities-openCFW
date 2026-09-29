
int am_devices_mspi_read(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_2c [24];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0048949c(auStack_2c,0x18);
  uVar1 = DAT_0059d1c8;
  iVar2 = uled_rw_param_validate(param_1,DAT_0059d1c8);
  if (iVar2 == 0) {
    am_devices_mspi_set_serail_mode(*DAT_0059d1cc,*(undefined4 *)(param_1 + 0x18));
    mspi_transfer_build(param_1,auStack_2c,0);
    iVar2 = FUN_004c2098(*(undefined4 *)(param_1 + 0x18),auStack_2c,DAT_0059d1d0);
    if (iVar2 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,uVar1,0xc0,DAT_0059d1d4,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0059d1d8,DAT_0059d1d8,iVar2);
      }
    }
    am_devices_mspi_set_quad_mode(*DAT_0059d1dc,*(undefined4 *)(param_1 + 0x18));
  }
  return iVar2;
}

