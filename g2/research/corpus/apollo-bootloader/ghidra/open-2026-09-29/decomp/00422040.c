
longlong FUN_00422040(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004215dc(5,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = critical_save();
    FUN_00421632(5,param_1,0);
    iVar2 = FUN_004215ae(5);
    if (iVar2 == 0) {
      if (*DAT_004222dc != 0) {
        *DAT_00422458 = 0;
        clkgen_disable_426d1e();
        FUN_00421cce(0x36);
        FUN_00421b5c(0x36);
        *DAT_00422450 = 0;
        *DAT_00422454 = 0;
      }
      dual_switch_426c8c(0);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

