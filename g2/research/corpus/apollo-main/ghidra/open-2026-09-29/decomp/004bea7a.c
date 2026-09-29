
undefined8
_anccGetNextNotificationHandler(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  ushort *puVar3;
  uint uVar4;
  
  uVar4 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar4 = 0xd4;
    param_2 = DAT_004bf214;
    FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf218,0xd4,DAT_004bf214,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004bf224,DAT_004bf224,param_1 & 0xff,uVar4,param_2,param_3);
  }
  puVar3 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar3 != (ushort *)0x0) {
    *(char *)(puVar3 + 1) = (char)param_1;
    pbVar1 = DAT_004bf6c0;
    *puVar3 = (ushort)*DAT_004bf6c0;
    WsfMsgSend(pbVar1[1],puVar3);
  }
  return CONCAT44(param_2,uVar4);
}

