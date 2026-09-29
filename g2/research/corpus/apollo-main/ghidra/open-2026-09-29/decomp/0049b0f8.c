
undefined4
SVC_KvdbWriteTemperatureUnit
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_0049b168;
  uVar5 = param_1[1];
  uVar6 = param_1[2];
  *DAT_0049b168 = *param_1;
  puVar1[1] = uVar5;
  puVar1[2] = uVar6;
  *(undefined1 *)puVar1 = 1;
  uVar2 = FUN_0049acd4(puVar1,8,0,uVar6,param_1,param_2,param_3,param_4);
  *(undefined2 *)(puVar1 + 2) = uVar2;
  iVar3 = SVC_KvdbBlobWrite(PTR_s_kvTemperatureUnit_0049b16c,puVar1,0xc);
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_kv_tu_0049b17c,DAT_0049b178,DAT_0049b190,0x35,DAT_0049b18c,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0049b194,DAT_0049b194,iVar3);
    }
  }
  return 0;
}

