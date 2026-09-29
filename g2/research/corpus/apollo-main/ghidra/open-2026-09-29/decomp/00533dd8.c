
undefined8 attsProcValueCnf(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*(short *)(param_1 + 0x26) != 0) {
    WsfTimerStop(param_1);
    puVar1 = (undefined4 *)attsFindByHandle(*(undefined2 *)(param_1 + 0x26),&uStack_10);
    if (((puVar1 != (undefined4 *)0x0) && (iVar2 = FUN_004751c8(*puVar1,DAT_00533eb4,2), iVar2 == 0)
        ) && (iVar2 = AttsCsfGetChangeAwareState(*(undefined1 *)(param_1 + 0x24)), iVar2 != 0)) {
      AttsCsfSetClientsChangeAwarenessState(*(undefined1 *)(param_1 + 0x24),0);
    }
    *(undefined2 *)(param_1 + 0x26) = 0;
    if (-1 < (int)((uint)*(byte *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4 +
                                  2) << 0x1e)) {
      attsExecCallback(*(undefined1 *)(param_1 + 0x24),*(undefined2 *)(param_1 + 0x28),0);
      *(undefined2 *)(param_1 + 0x28) = 0;
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}

