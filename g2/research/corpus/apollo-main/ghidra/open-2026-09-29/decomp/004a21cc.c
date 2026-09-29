
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 APP_MasterScanEvent(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  ushort *puVar3;
  uint uVar4;
  
  uVar4 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar4 = 0x498;
    param_2 = DAT_004a28d8;
    FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,_DAT_004a2910,0x498,DAT_004a28d8,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a28e0,DAT_004a28e0,param_1 & 0xff,uVar4,param_2,param_3);
  }
  puVar3 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar3 != (ushort *)0x0) {
    *(undefined1 *)(puVar3 + 1) = 0xb2;
    piVar1 = DAT_004a2648;
    *puVar3 = (ushort)*(byte *)(*DAT_004a2648 + 0x55);
    puVar3[4] = (ushort)param_1 & 0xff;
    WsfMsgSend(*(undefined1 *)(*piVar1 + 0x56),puVar3);
  }
  return CONCAT44(param_2,uVar4);
}

