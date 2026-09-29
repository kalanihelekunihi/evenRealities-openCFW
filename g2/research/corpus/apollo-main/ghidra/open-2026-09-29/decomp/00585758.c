
void SVC_KvdbWriteTime(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  int iVar3;
  
  puVar1 = DAT_00585808;
  DAT_00585808[8] = (char)param_2;
  *(undefined4 *)(puVar1 + 4) = param_1;
  *puVar1 = 3;
  uVar2 = FUN_0049acd4(puVar1,10,0,param_4,param_1,param_2,param_3,param_4);
  *(undefined2 *)(puVar1 + 10) = uVar2;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0058581c,DAT_00585818,DAT_00585838,0x41,DAT_00585834,
                 *(undefined2 *)(puVar1 + 10));
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_005857ae;
  }
  compress_log_output(0x10400000,DAT_0058583c,DAT_0058583c,*(undefined2 *)(puVar1 + 10));
LAB_005857ae:
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0058581c,DAT_00585818,DAT_00585838,0x42,DAT_0058582c,(int)(char)puVar1[8],
                 *(undefined4 *)(puVar1 + 4));
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_00585830,DAT_00585830,(int)(char)puVar1[8],
                        *(undefined4 *)(puVar1 + 4));
  }
  SVC_KvdbBlobWrite(DAT_0058580c,puVar1,0xc);
  return;
}

