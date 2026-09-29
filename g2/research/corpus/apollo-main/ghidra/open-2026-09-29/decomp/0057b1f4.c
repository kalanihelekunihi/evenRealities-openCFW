
undefined8 SVC_PcmRecoderProcess(uint param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  iVar2 = DAT_0057b40c;
  uVar4 = param_1;
  uVar5 = param_2;
  if ((param_1 & 0xff) < 2) {
    iVar3 = param_3;
    if (*(char *)((param_1 & 0xff) * 0xc + DAT_0057b40c + 10) == '\0') {
      service_audio_recording_start(param_1 & 0xff);
    }
    if (((*(int *)(iVar2 + (param_1 & 0xff) * 0xc) == 0) ||
        (DAT_0057b42c <= (uint)(param_3 + *(int *)((param_1 & 0xff) * 0xc + iVar2 + 4)))) &&
       (iVar1 = service_audio_recording_open_next(param_1 & 0xff), iVar1 != 0)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar4 = 0x18a;
        uVar5 = DAT_0057b430;
        FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b434);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0057b438,DAT_0057b438);
      }
    }
    else {
      iVar3 = file_write(param_2,1,param_3,*(undefined4 *)(iVar2 + (param_1 & 0xff) * 0xc),uVar4,
                         uVar5,iVar3,param_4);
      if (iVar3 == param_3) {
        *(int *)((param_1 & 0xff) * 0xc + iVar2 + 4) =
             param_3 + *(int *)(iVar2 + (param_1 & 0xff) * 0xc + 4);
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uVar4 = 0x197;
          uVar5 = DAT_0057b43c;
          FUN_0043d574(1,DAT_0057b388,DAT_0057b384,DAT_0057b434,0x197,DAT_0057b43c,param_1 & 0xff);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057b440,DAT_0057b440,param_1 & 0xff);
        }
        file_close(*(undefined4 *)(iVar2 + (param_1 & 0xff) * 0xc));
        *(undefined4 *)(iVar2 + (param_1 & 0xff) * 0xc) = 0;
      }
    }
  }
  return CONCAT44(uVar5,uVar4);
}

