
longlong FUN_00421e4a(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004215dc(4,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = critical_save();
    FUN_00421632(4,param_1,0);
    iVar2 = FUN_004215ae(4);
    if (iVar2 == 0) {
      clkgen_hfadj_enable_426c58(0);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

