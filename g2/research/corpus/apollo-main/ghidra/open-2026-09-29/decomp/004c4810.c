
undefined8
APP_BleRingHandlerInit(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = param_2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x98;
    param_3 = DAT_004c4c8c;
    FUN_0043d574(4,DAT_004c4c78,DAT_004c4c74,DAT_004c4c90,0x98,DAT_004c4c8c,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004c4c94);
  }
  puVar1 = DAT_004c4c68;
  DAT_004c4c68[1] = param_1;
  *puVar1 = 0;
  *(undefined2 *)(puVar1 + 8) = 1;
  *(undefined4 *)(puVar1 + 4) = param_2;
  **(undefined2 **)(puVar1 + 4) = 0x10;
  *(undefined2 *)(*(int *)(puVar1 + 4) + 2) = 0x12;
  *(undefined2 *)(*(int *)(puVar1 + 4) + 4) = 0x13;
  return CONCAT44(param_3,uVar3);
}

