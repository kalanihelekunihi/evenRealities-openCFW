
void service_audio_recording_start
               (byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_38 [32];
  undefined4 uStack_18;
  
  if (param_1 < 2) {
    uStack_18 = param_4;
    service_audio_recording_directory_prepare();
    iVar1 = DAT_0057b40c;
    FUN_0043c0e4(DAT_0057b40c + (uint)param_1 * 0xc,0xc,0);
    *(undefined1 *)((uint)param_1 * 0xc + iVar1 + 0xb) = 1;
    FUN_0043c0e4(auStack_38,0x20,0);
    *(undefined2 *)((uint)param_1 * 0xc + iVar1 + 8) = 0;
    while (*(short *)((uint)param_1 * 0xc + iVar1 + 8) == 0) {
      service_audio_format_recording_path
                (param_1,*(undefined2 *)((uint)param_1 * 0xc + iVar1 + 8),auStack_38,0x20);
      iVar2 = file_open(auStack_38,&DAT_0057b378);
      if (iVar2 == 0) break;
      file_close();
      *(short *)((uint)param_1 * 0xc + iVar1 + 8) = *(short *)((uint)param_1 * 0xc + iVar1 + 8) + 1;
    }
    if (*(short *)((uint)param_1 * 0xc + iVar1 + 8) != 0) {
      *(undefined2 *)((uint)param_1 * 0xc + iVar1 + 8) = 0;
    }
    *(undefined1 *)(iVar1 + (uint)param_1 * 0xc + 10) = 1;
  }
  return;
}

