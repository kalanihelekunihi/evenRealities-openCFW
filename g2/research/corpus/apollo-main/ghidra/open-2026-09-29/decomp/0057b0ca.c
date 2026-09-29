
void service_audio_recording_directory_prepare(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  undefined1 auStack_118 [264];
  undefined4 uStack_10;
  
  uVar2 = DAT_0057b41c;
  uVar1 = DAT_0057b400;
  uStack_10 = in_r3;
  iVar3 = FUN_004cfa8a(DAT_0057b41c,DAT_0057b400,auStack_118);
  if ((iVar3 == -2) && (iVar3 = FUN_004cfc5c(uVar2,uVar1), iVar3 != 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b424,0x155,DAT_0057b420);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0057b428);
    }
  }
  return;
}

