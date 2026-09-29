
undefined4
SVC_KvdbWriteAlsScale(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  puVar1 = DAT_004aedf8;
  uVar5 = param_1[1];
  uVar6 = param_1[2];
  *DAT_004aedf8 = *param_1;
  puVar1[1] = uVar5;
  puVar1[2] = uVar6;
  *(undefined1 *)puVar1 = 1;
  uVar2 = FUN_0049acd4(puVar1,8,0,uVar6,param_1,param_2,param_3,param_4);
  *(undefined2 *)(puVar1 + 2) = uVar2;
  iVar3 = SVC_KvdbBlobWrite(PTR_s_kvAlsScale_004aedfc,puVar1,0xc);
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_kv_als_scale_004aee0c,DAT_004aee08,DAT_004aee20,0x32,DAT_004aee1c,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004aee24,DAT_004aee24,iVar3);
    }
  }
  return 0;
}

