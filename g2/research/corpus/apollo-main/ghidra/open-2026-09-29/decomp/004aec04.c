
undefined4
SVC_KvdbWriteSetting(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_004aec74;
  FUN_00439c04(DAT_004aec74,param_1,0x1c,param_4,param_1,param_2,param_3,param_4);
  *puVar1 = 4;
  uVar2 = FUN_0049acd4(puVar1,0x18,0);
  *(undefined2 *)(puVar1 + 0x18) = uVar2;
  iVar3 = SVC_KvdbBlobWrite(PTR_s_kvSetting_004aec78,puVar1,0x1c);
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_kv_tz_004aec88,DAT_004aec84,DAT_004aec9c,0x43,DAT_004aec98,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004aeca0,DAT_004aeca0,iVar3);
    }
  }
  return 0;
}

