
int am_devices_mspi_qspi_write_async
              (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_34;
  undefined1 local_33;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  uVar1 = DAT_0059d1f8;
  iVar5 = -1;
  uStack_1c = param_4;
  iVar2 = uled_rw_param_validate(param_1,DAT_0059d1f8);
  if (iVar2 == 0) {
    am_devices_mspi_set_quad_mode(*DAT_0059d1dc,*(undefined4 *)(param_1 + 0x18));
    am_hal_mspi_interrupt_clear(*(undefined4 *)(param_1 + 0x18),0x1a80);
    FUN_004c2328(*(undefined4 *)(param_1 + 0x18),0x1a80);
    local_3c = *(undefined4 *)(param_1 + 0x14);
    local_38 = *(undefined4 *)(param_1 + 0xc);
    FUN_0047510e(&local_3c);
    FUN_0043c0e4(&local_34,0x18,0);
    local_34 = 1;
    local_33 = 1;
    local_2c = *(undefined4 *)(param_1 + 4);
    local_28 = *(undefined4 *)(param_1 + 0x14);
    local_30 = *(undefined4 *)(param_1 + 0xc);
    local_24 = 0;
    local_20 = 0;
    iVar2 = FUN_004c2208(*(undefined4 *)(param_1 + 0x18),&local_34,1,DAT_0059d200,DAT_0059d1fc);
    iVar3 = osSemaphoreAcquire(*DAT_0059d164,3000);
    if (iVar3 == 0) {
      iVar5 = 0;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,uVar1,0x12a,DAT_0059d204,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0059d208,DAT_0059d208,iVar3);
      }
    }
    am_devices_mspi_set_serail_mode(*DAT_0059d1cc,*(undefined4 *)(param_1 + 0x18));
    if (iVar5 != 0) {
      iVar2 = iVar5;
    }
  }
  return iVar2;
}

