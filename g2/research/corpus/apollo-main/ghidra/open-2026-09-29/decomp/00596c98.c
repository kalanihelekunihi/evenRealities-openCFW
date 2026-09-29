
undefined4 FUN_00596c98(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 local_28;
  undefined4 local_24;
  uint local_20;
  int local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  if (param_2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_24 = DAT_00597050;
      local_28 = 0x77;
      FUN_0043d574(1,DAT_00597028,DAT_00597024,DAT_00597054);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00597058);
    }
    return 0xffffffff;
  }
  bVar1 = translate_ui_0059db5c();
  if (bVar1 == 2) {
    local_1c = 0;
    local_20 = 0;
    FUN_00443504(&local_20,&local_1c);
    if ((local_1c != 5) && (local_20 != 5)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_24 = DAT_0059705c;
        local_28 = 0x85;
        FUN_0043d574(2,DAT_00597028,DAT_00597024,DAT_00597054);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00597060,DAT_00597060);
      }
      AUDM_appRelease(1);
      FUN_0043c0e4(DAT_00597044,0x10,0);
      translate_ui_0059d9d4();
      bVar1 = translate_ui_0059db5c();
    }
  }
  if (bVar1 == 0) {
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      local_18 = *DAT_00597064;
      uStack_14 = DAT_00597064[1];
      FUN_0048eb32(DAT_00597068,2,&local_18);
    }
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      FUN_0045a8ee(5,0,0,500);
    }
  }
  else {
    if (bVar1 != 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_1c = translate_ui_0059db66(bVar1);
        local_20 = (uint)bVar1;
        local_24 = DAT_00597084;
        local_28 = 0x9d;
        FUN_0043d574(1,DAT_00597028,DAT_00597024,DAT_00597054);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        local_28 = translate_ui_0059db66(bVar1);
        compress_log_output(0x4800000,PTR_s__translate_fsm_translate_ui_stat_00597088,
                            PTR_s__translate_fsm_translate_ui_stat_00597088,bVar1);
      }
      return 0xffffffff;
    }
    if (*(char *)(param_2 + 0x10) == '\b') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_24 = DAT_00597074;
        local_28 = 0x96;
        FUN_0043d574(1,DAT_00597028,DAT_00597024,DAT_00597054);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00597078,DAT_00597078);
      }
      iVar2 = FUN_0045a568();
      if (iVar2 == 1) {
        local_28 = *DAT_0059707c;
        local_24 = DAT_0059707c[1];
        FUN_0048eb32(DAT_00597080,2,&local_28);
      }
      FUN_0059ec28(8,1);
    }
    else {
      FUN_0059ec28(4,0);
    }
  }
  *DAT_00597044 = 1;
  FUN_0059e9e2();
  FUN_0043c0e4(param_1 + 1,8,0);
  FUN_00439be4(param_1 + 1,param_2 + 4,*(undefined2 *)(param_2 + 2));
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_20 = param_1 + 1;
    local_24 = DAT_0059706c;
    local_28 = 0xa7;
    FUN_0043d574(4,DAT_00597028,DAT_00597024,DAT_00597054);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00597070,DAT_00597070,param_1 + 1);
  }
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 0xc);
  if (*(int *)(param_1 + 0xc) != 0) {
    AUDM_appAcquire(1);
  }
  return 0;
}

