
longlong FUN_00421cce(undefined1 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  uint local_10;
  uint local_c;
  
  local_10 = param_3;
  local_c = param_4;
  iVar2 = FUN_004215dc(2,param_1);
  if (iVar2 != 0) {
    local_c = critical_save();
    FUN_00421632(2,param_1,0);
    iVar2 = FUN_004215ae(2);
    if (iVar2 == 0) {
      local_10 = CONCAT31(local_10._1_3_,1);
      FUN_0041d3e4(4,&local_10);
      *DAT_00422444 = 0;
      *DAT_00422448 = 0;
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_c & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

