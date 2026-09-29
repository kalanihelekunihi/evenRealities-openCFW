
longlong FUN_00421b5c(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004215dc(3,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = critical_save();
    FUN_00421632(3,param_1,0);
    iVar2 = FUN_004215ae(3);
    if (iVar2 == 0) {
      FUN_0041d92c(0xf,*DAT_00422440);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

