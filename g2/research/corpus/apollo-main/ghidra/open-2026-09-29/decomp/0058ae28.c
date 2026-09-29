
undefined8 teleprompt_request_page_data(undefined4 param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = param_2;
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    iVar1 = page_data_lock();
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xcc;
        FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b958,0xcc,DAT_0058b960,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0058b964,DAT_0058b964,param_1);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = request_page_data_locked(param_1,param_2 & 0xff);
      semantic_page_data_unlock();
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 200;
      FUN_0043d574(4,DAT_0058b354,DAT_0058b350,DAT_0058b958,200,DAT_0058b8ec,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0058b95c,DAT_0058b95c,param_1);
    }
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

