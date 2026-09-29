
undefined8 APP_MasterSetPhyEvent(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  ushort *puVar4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar3 = FUN_0043d0ce();
  uVar2 = DAT_004a2c78;
  if (iVar3 << 0x1e < 0) {
    unaff_r5 = 0x4b4;
    FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,DAT_004a2c7c);
    unaff_r6 = uVar2;
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004a2c80,DAT_004a2c80);
  }
  puVar4 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar4 != (ushort *)0x0) {
    *(undefined1 *)(puVar4 + 1) = 0xb4;
    piVar1 = DAT_004a2648;
    *puVar4 = (ushort)*(byte *)(*DAT_004a2648 + 0x55);
    puVar4[4] = 0;
    WsfMsgSend(*(undefined1 *)(*piVar1 + 0x56),puVar4);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

