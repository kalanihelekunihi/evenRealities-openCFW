
void AUDM_SendSyncMsgToPeer(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined1 local_c;
  undefined3 uStack_b;
  
  _local_c = CONCAT31((int3)((uint)param_4 >> 8),(char)param_1);
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar2 = 0x72;
    param_2 = DAT_0054f9d0;
    FUN_0043d574(3,DAT_0054f988,DAT_0054f984,DAT_0054f9d4,0x72,DAT_0054f9d0,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__service_audio_manager_sending_a_0054f9d8,
                        PTR_s__service_audio_manager_sending_a_0054f9d8,param_1 & 0xff,uVar2,param_2
                        ,param_3);
  }
  FUN_004651e0(0x10c,&local_c,1,0);
  return;
}

