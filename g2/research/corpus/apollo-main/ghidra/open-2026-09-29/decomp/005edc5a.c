
undefined4 tracepoint_scan_files(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 in_r3;
  undefined4 local_6c;
  undefined1 auStack_68 [80];
  undefined4 uStack_18;
  
  iVar2 = DAT_005ee794;
  uStack_18 = in_r3;
  FUN_0043c0e4(DAT_005ee794,0x88,0);
  uVar3 = DAT_005ee884;
  iVar1 = file_opendir(DAT_005ee884);
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005ee79c,DAT_005ee798,DAT_005ee7a4,0x85,DAT_005ee7a0,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005ee7a8,DAT_005ee7a8,uVar3);
    }
    uVar3 = 0xffffffff;
  }
  else {
    while (iVar4 = file_readdir(iVar1), iVar4 != 0) {
      local_6c = 0;
      if ((*(char *)(iVar4 + 0x100) == '\b') &&
         (iVar5 = tracepoint_parse_file_sequence(iVar4,&local_6c), iVar5 != 0)) {
        tracepoint_format_file_path(auStack_68,0x50,local_6c);
        uVar3 = tracepoint_get_file_size(auStack_68);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005ee7a4,0x96,DAT_005ee7ac,iVar4,local_6c,
                       uVar3);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10c00000,DAT_005ee7b0,DAT_005ee7b0,iVar4,local_6c,uVar3);
        }
        tracepoint_insert_file_sorted(local_6c,uVar3);
      }
    }
    file_closedir(iVar1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005ee7a4,0x9d,DAT_005ee888,
                   *(undefined4 *)(iVar2 + 0x80),*(undefined4 *)(iVar2 + 0x84));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_005ee88c,DAT_005ee88c,*(undefined4 *)(iVar2 + 0x80),
                          *(undefined4 *)(iVar2 + 0x84));
    }
    uVar3 = 0;
  }
  return uVar3;
}

