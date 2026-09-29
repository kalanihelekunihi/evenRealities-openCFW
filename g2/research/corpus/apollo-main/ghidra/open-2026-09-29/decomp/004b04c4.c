
undefined4
SVC_KvdbWriteTerminalMode
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_004b0530;
  *DAT_004b0530 = *param_1;
  *(undefined1 *)puVar1 = 1;
  uVar2 = FUN_0049acd4(puVar1,2,0,param_4,param_1,param_2,param_3,param_4);
  *(undefined2 *)((int)puVar1 + 2) = uVar2;
  iVar3 = SVC_KvdbBlobWrite(PTR_s_kvTerminalMode_004b0534,puVar1,4);
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_kv_terminal_mode_004b0544,DAT_004b0540,DAT_004b0558,0x30,DAT_004b0554,
                   iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004b055c,DAT_004b055c,iVar3);
    }
  }
  return 0;
}

