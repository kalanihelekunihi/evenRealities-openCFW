
void service_audio_recording_stop(byte param_1)

{
  int iVar1;
  
  iVar1 = DAT_0057b40c;
  if (param_1 < 2) {
    if (*(int *)(DAT_0057b40c + (uint)param_1 * 0xc) != 0) {
      file_close(*(undefined4 *)(DAT_0057b40c + (uint)param_1 * 0xc));
      *(undefined4 *)(iVar1 + (uint)param_1 * 0xc) = 0;
    }
    *(undefined1 *)(iVar1 + (uint)param_1 * 0xc + 10) = 0;
  }
  return;
}

