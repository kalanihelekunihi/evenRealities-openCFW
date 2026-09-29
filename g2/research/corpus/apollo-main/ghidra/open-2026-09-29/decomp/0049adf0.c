
undefined4
SVC_KvdbWriteUniversalSetting
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_0049ae60;
  FUN_00439be4(DAT_0049ae60,param_1,0x14,param_4,param_1,param_2,param_3,param_4);
  *puVar1 = 3;
  uVar2 = FUN_0049acd4(puVar1,0x12,0);
  *(undefined2 *)(puVar1 + 0x12) = uVar2;
  iVar3 = SVC_KvdbBlobWrite(PTR_s_kvUniversalSetting_0049ae64,puVar1,0x14);
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_kvdb_universal_setting_0049ae74,DAT_0049ae70,DAT_0049ae88,0x39,
                   DAT_0049ae84,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0049ae8c,DAT_0049ae8c,iVar3);
    }
  }
  return 0;
}

