
undefined4
teleprompt_page_data_get(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = page_data_lock(0);
  iVar2 = DAT_0058bc08;
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bca8,0x1c8,DAT_0058bca4,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0058bcac,DAT_0058bcac,param_1);
    }
    uVar3 = 0;
  }
  else if (param_1 < *(uint *)(DAT_0058bc08 + 0x5190)) {
    iVar1 = semantic_page_to_slot(param_1);
    iVar4 = semantic_slot_loaded(iVar1,param_1);
    uVar3 = DAT_0058bcb0;
    if (iVar4 == 0) {
      semantic_page_data_unlock();
      uVar3 = 0;
    }
    else {
      FUN_00439be4(DAT_0058bcb0,iVar2 + iVar1 * 0x414,0x40c);
      semantic_page_data_unlock();
    }
  }
  else {
    semantic_page_data_unlock();
    uVar3 = 0;
  }
  return uVar3;
}

