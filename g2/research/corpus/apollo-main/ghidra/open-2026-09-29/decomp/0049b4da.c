
undefined4 setting_build_full_status_package(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  undefined4 uVar4;
  
  if (param_1 != (undefined1 *)0x0) {
    FUN_0043c0e4(param_1,0x68,0);
    *param_1 = 2;
    *(undefined2 *)(param_1 + 8) = 4;
    if (*(short *)(DAT_0049bdf4 + 8) == 4) {
      param_1[0xc] = *(undefined1 *)(DAT_0049bdf4 + 0xc);
    }
    else {
      param_1[0xc] = 0;
    }
    iVar1 = settings_get_config();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xbf,DAT_0049bfa0,
                   *(undefined1 *)(iVar1 + 2),*(undefined1 *)(iVar1 + 1),*(undefined1 *)(iVar1 + 8),
                   *(undefined1 *)(iVar1 + 9));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_0049bfa4,DAT_0049bfa4,*(undefined1 *)(iVar1 + 2),
                          *(undefined1 *)(iVar1 + 1),*(undefined1 *)(iVar1 + 8),
                          *(undefined1 *)(iVar1 + 9));
    }
    *(uint *)(param_1 + 0x60) = (uint)*(byte *)(iVar1 + 2);
    *(uint *)(param_1 + 0x10) = (uint)*(byte *)(iVar1 + 1);
    *(uint *)(param_1 + 0x14) = (uint)*(byte *)(iVar1 + 8);
    *(uint *)(param_1 + 0x18) = (uint)*(byte *)(iVar1 + 9);
    FUN_0044b5a0(param_1 + 0x28,DAT_0049bfa8,0xb);
    pcVar3 = (char *)settings_get_runtime();
    if ((pcVar3 == (char *)0x0) || (*pcVar3 == '\0')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xd1,DAT_0049bfac);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0049bfb0,DAT_0049bfb0);
      }
      SVC_Settings_RequestLeftVersion();
    }
    else {
      FUN_0044b5a0(param_1 + 0x1c,pcVar3,0xb);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xd8,DAT_0049bfb4,param_1 + 0x1c,
                   param_1 + 0x28);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0049bfb8,DAT_0049bfb8,param_1 + 0x1c,param_1 + 0x28);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xdb,DAT_0049bfbc,
                   *(undefined1 *)(iVar1 + 10),*(undefined4 *)(iVar1 + 0xc),
                   *(undefined4 *)(iVar1 + 0x10));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0049bfc0,DAT_0049bfc0,*(undefined1 *)(iVar1 + 10),
                          *(undefined4 *)(iVar1 + 0xc),*(undefined4 *)(iVar1 + 0x10));
    }
    *(uint *)(param_1 + 0x34) = (uint)*(byte *)(iVar1 + 10);
    *(undefined4 *)(param_1 + 0x38) = *(undefined4 *)(iVar1 + 0xc);
    *(uint *)(param_1 + 0x40) = (uint)*(byte *)(iVar1 + 0x14);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xe1,DAT_0049bfc4,
                   *(undefined4 *)(iVar1 + 0x34),*(undefined4 *)(iVar1 + 0x38),
                   *(undefined4 *)(iVar1 + 0x3c),*(undefined1 *)(iVar1 + 0x15));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_0049bfc8,DAT_0049bfc8,*(undefined4 *)(iVar1 + 0x34),
                          *(undefined4 *)(iVar1 + 0x38),*(undefined4 *)(iVar1 + 0x3c),
                          *(undefined1 *)(iVar1 + 0x15));
    }
    *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(iVar1 + 0x34);
    *(undefined4 *)(param_1 + 0x48) = *(undefined4 *)(iVar1 + 0x38);
    *(undefined4 *)(param_1 + 0x4c) = *(undefined4 *)(iVar1 + 0x3c);
    *(uint *)(param_1 + 0x50) = (uint)*(byte *)(iVar1 + 0x15);
    *(uint *)(param_1 + 0x54) = (uint)*(byte *)(iVar1 + 0x16);
    *(uint *)(param_1 + 0x58) = (uint)*(byte *)(iVar1 + 0x17);
    *(undefined4 *)(param_1 + 0x5c) = *(undefined4 *)(iVar1 + 0x40);
    uVar4 = service_ancc_message_count_get();
    *(undefined4 *)(param_1 + 100) = uVar4;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xf1,DAT_0049bfcc,
                   *(undefined4 *)(param_1 + 100));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0049bfd0,DAT_0049bfd0,*(undefined4 *)(param_1 + 100));
    }
    return 1;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bf1c,0xab,DAT_0049bf18);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_0049bf20,DAT_0049bf20);
  }
  return 0;
}

