
void teleprompt_page_data_init(uint param_1,uint param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_0058b344;
  if ((param_2 == 0) || (param_2 <= param_1)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058bc20,0x14d,DAT_0058bc1c,param_2,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0058bc24,DAT_0058bc24,param_2,param_1);
    }
  }
  else {
    if (*DAT_0058b344 == 0) {
      iVar2 = osMutexNew(0);
      *piVar1 = iVar2;
      if (*piVar1 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058bc20,0x154,DAT_0058bc28);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return;
        }
        compress_log_output(0x4000000,DAT_0058bc2c,DAT_0058bc2c);
        return;
      }
    }
    iVar3 = page_data_lock();
    iVar2 = DAT_0058b530;
    if (iVar3 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058bc20,0x15a,DAT_0058bc30);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058bc34,DAT_0058bc34);
      }
    }
    else {
      FUN_0043c0e4(DAT_0058b530,0x51a4,0);
      *(uint *)(iVar2 + 0x5190) = param_2;
      *(undefined1 *)(iVar2 + 0x51a0) = 1;
      semantic_page_data_unlock();
      if (param_1 == 0) {
        iVar2 = 0;
      }
      else {
        iVar2 = param_1 - 1;
      }
      uVar4 = semantic_clamp_window_start(iVar2);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058bc20,0x165,DAT_0058bc38,param_1,param_2,
                     uVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xcc00000,DAT_0058bc3c,DAT_0058bc3c,param_1,param_2,uVar4);
      }
      teleprompt_page_data_set_window(uVar4);
    }
  }
  return;
}

