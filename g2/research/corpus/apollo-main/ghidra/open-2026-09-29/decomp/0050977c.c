
undefined4 _nvdbUpdataSensorCaldata(void)

{
  int iVar1;
  undefined4 in_r3;
  char acStack_68 [88];
  short sStack_10;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_00509b0c,DAT_00509b08,DAT_00509b04,0x3e,DAT_00509b00);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_00509b10,DAT_00509b10);
  }
  iVar1 = SVC_NvdbRead(PTR_s_nvSCald_00509b14,acStack_68,0x5c);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00509b0c,DAT_00509b08,DAT_00509b04,0x41,PTR_s_version__d__d__00509b18,
                   acStack_68[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__nv_s_cald_version__d__d__00509b1c,
                          PTR_s__nv_s_cald_version__d__d__00509b1c,acStack_68[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00509b0c,DAT_00509b08,DAT_00509b04,0x42,PTR_s_crc_0x_x_0x_x__00509b20,
                   sStack_10,*(undefined2 *)(DAT_00509afc + 0x58));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__nv_s_cald_crc_0x_x_0x_x__00509b24,
                          PTR_s__nv_s_cald_crc_0x_x_0x_x__00509b24,sStack_10,
                          *(undefined2 *)(DAT_00509afc + 0x58));
    }
    if ((sStack_10 != *(short *)(DAT_00509afc + 0x58)) && (acStack_68[0] == '\0')) {
      nvdbSensorCaldataUpdate
                (*(undefined4 *)(DAT_00509afc + 0x3c),DAT_00509afc + 4,DAT_00509afc + 0x10,
                 DAT_00509afc + 0x1c,DAT_00509afc + 0x2c,DAT_00509afc + 0x40);
    }
    return 0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00509b0c,DAT_00509b08,DAT_00509b04,0x49,
                 PTR_s_____>not_key_in_the_flash__first_00509b28,
                 *(undefined2 *)(DAT_00509afc + 0x58));
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__nv_s_cald_____>not_key_in_the_f_00509b2c,
                        PTR_s__nv_s_cald_____>not_key_in_the_f_00509b2c,
                        *(undefined2 *)(DAT_00509afc + 0x58));
  }
  nvdbSensorCaldataUpdate
            (*(undefined4 *)(DAT_00509afc + 0x3c),DAT_00509afc + 4,DAT_00509afc + 0x10,
             DAT_00509afc + 0x1c,DAT_00509afc + 0x2c,DAT_00509afc + 0x40);
  return 0;
}

