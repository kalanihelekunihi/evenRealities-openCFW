
int boot_low_level_reconfigure(void)

{
  byte bVar1;
  int iVar2;
  int unaff_r4;
  int unaff_r5;
  int *unaff_r6;
  undefined4 unaff_r7;
  undefined4 *unaff_r8;
  
  iVar2 = am_hal_mspi_device_configure();
  if (iVar2 == 0) {
    iVar2 = am_hal_mspi_enable(*unaff_r8);
    if (iVar2 == 0) {
      FUN_0041ff34(0);
      FUN_0041fadc();
      FUN_0041d90e(0x67,&stack0x00000008);
      iVar2 = am_hal_mspi_interrupt_clear(*unaff_r8,0x1a80);
      if (iVar2 == 0) {
        iVar2 = am_hal_mspi_interrupt_enable(*unaff_r8,0x1a80);
        if (iVar2 == 0) {
          FUN_0041fdde(0x15,4);
          FUN_0041fdc0(0x15);
          FUN_0041b8e0();
          iVar2 = DAT_00420b04;
          *(undefined4 *)(DAT_00420b04 + unaff_r4 * 0x10) = unaff_r7;
          if (unaff_r5 == 0) {
            bVar1 = *(byte *)(DAT_00420c38 + 8);
          }
          else {
            bVar1 = *(byte *)(unaff_r5 + 8);
          }
          *(uint *)(unaff_r4 * 0x10 + iVar2 + 4) = (uint)bVar1;
          *(undefined4 *)(unaff_r4 * 0x10 + iVar2 + 8) = *unaff_r8;
          *(undefined1 *)(unaff_r4 * 0x10 + iVar2 + 0xc) = 1;
          *unaff_r6 = iVar2 + unaff_r4 * 0x10;
          elog_output(3,DAT_00420adc,DAT_00420978,DAT_00420c1c);
          iVar2 = 0;
        }
        else {
          elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c);
          iVar2 = 1;
        }
      }
      else {
        iVar2 = 1;
      }
    }
    else {
      elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c);
      am_hal_mspi_deinitialize(*unaff_r8);
    }
  }
  else {
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c);
    am_hal_mspi_deinitialize(*unaff_r8);
  }
  return iVar2;
}

