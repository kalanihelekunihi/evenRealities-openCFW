
undefined4 service_audio_recording_open_next(byte param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 auStack_30 [32];
  
  iVar2 = DAT_0057b40c;
  if (*(int *)(DAT_0057b40c + (uint)param_1 * 0xc) != 0) {
    file_close(*(undefined4 *)(DAT_0057b40c + (uint)param_1 * 0xc));
    *(undefined4 *)(iVar2 + (uint)param_1 * 0xc) = 0;
  }
  if (*(char *)((uint)param_1 * 0xc + iVar2 + 0xb) == '\0') {
    *(short *)((uint)param_1 * 0xc + iVar2 + 8) = *(short *)((uint)param_1 * 0xc + iVar2 + 8) + 1;
    if (*(short *)((uint)param_1 * 0xc + iVar2 + 8) != 0) {
      *(undefined2 *)((uint)param_1 * 0xc + iVar2 + 8) = 0;
    }
  }
  else {
    *(undefined1 *)((uint)param_1 * 0xc + iVar2 + 0xb) = 0;
  }
  service_audio_format_recording_path
            (param_1,*(undefined2 *)((uint)param_1 * 0xc + iVar2 + 8),auStack_30,0x20);
  uVar1 = file_open(auStack_30,&DAT_0057b1f0);
  *(undefined4 *)(iVar2 + (uint)param_1 * 0xc) = uVar1;
  if (*(int *)(iVar2 + (uint)param_1 * 0xc) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b414,0x146,DAT_0057b410);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0057b418,DAT_0057b418);
    }
    uVar1 = 0xffffffff;
  }
  else {
    *(undefined4 *)(iVar2 + (uint)param_1 * 0xc + 4) = 0;
    uVar1 = 0;
  }
  return uVar1;
}

