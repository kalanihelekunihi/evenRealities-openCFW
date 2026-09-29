
undefined8
APP_MasterUnpairDevEvent
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  ushort *puVar3;
  undefined4 uVar4;
  
  uVar4 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar4 = 0x455;
    param_2 = DAT_004a28d8;
    param_3 = param_1;
    FUN_0043d574(4,DAT_004a1fc0,DAT_004a1fbc,DAT_004a28dc,0x455,DAT_004a28d8,param_1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a28e0,DAT_004a28e0,param_1,uVar4,param_2,param_3);
  }
  puVar3 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar3 != (ushort *)0x0) {
    *(undefined1 *)(puVar3 + 1) = 0xb1;
    piVar1 = DAT_004a2648;
    *puVar3 = (ushort)*(byte *)(*DAT_004a2648 + 0x55);
    *(undefined4 *)(puVar3 + 2) = param_1;
    WsfMsgSend(*(undefined1 *)(*piVar1 + 0x56),puVar3);
  }
  return CONCAT44(param_2,uVar4);
}

