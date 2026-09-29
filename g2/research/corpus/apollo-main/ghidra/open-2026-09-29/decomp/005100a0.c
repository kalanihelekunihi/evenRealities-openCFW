
undefined8 CALLBACK_MGR_CreateNode(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = (undefined4 *)file_heap_allocate(8);
  if (puVar1 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x1b;
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_0051054c,0x1b,DAT_00510548);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510558,DAT_00510558);
    }
    puVar1 = (undefined4 *)0x0;
  }
  else {
    *puVar1 = param_1;
    puVar1[1] = 0;
  }
  return CONCAT44(param_3,puVar1);
}

