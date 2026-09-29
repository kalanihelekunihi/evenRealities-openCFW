
undefined8 FUN_00493606(undefined1 param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  
  if ((param_2 == 0) || (param_3 == 0)) {
    iVar1 = FUN_0043d0ce();
    iVar4 = param_3;
    if (iVar1 << 0x1e < 0) {
      iVar4 = 0x49;
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_0049402c,0x49,DAT_00494028);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004940a8,DAT_004940a8);
    }
    puVar2 = (undefined4 *)0x0;
  }
  else {
    iVar4 = param_3;
    iVar1 = file_heap_allocate(param_3);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar4 = 0x50;
        FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_0049402c,0x50,DAT_004940ac);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004940b0,DAT_004940b0);
      }
      puVar2 = (undefined4 *)0x0;
    }
    else {
      FUN_00439be4(iVar1,param_2,param_3);
      puVar2 = (undefined4 *)file_heap_allocate(0x14);
      if (puVar2 == (undefined4 *)0x0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          iVar4 = 0x5a;
          FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_0049402c,0x5a,DAT_004940b4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004940c4,DAT_004940c4);
        }
        file_heap_free(iVar1);
        puVar2 = (undefined4 *)0x0;
      }
      else {
        *(undefined1 *)(puVar2 + 2) = param_1;
        puVar2[3] = iVar1;
        *puVar2 = 0;
        puVar2[1] = 0;
      }
    }
  }
  return CONCAT44(iVar4,puVar2);
}

