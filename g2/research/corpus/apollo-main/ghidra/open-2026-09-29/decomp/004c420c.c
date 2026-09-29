
longlong FUN_004c420c(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004c37a8(5,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = FUN_00473940();
    FUN_004c37fe(5,param_1,0);
    iVar2 = FUN_004c377a(5);
    if (iVar2 == 0) {
      if (*DAT_004c44a8 != 0) {
        *DAT_004c4694 = 0;
        FUN_004d39e4();
        FUN_004c3e9a(0x36);
        FUN_004c3d28(0x36);
        *DAT_004c468c = 0;
        *DAT_004c4690 = 0;
      }
      FUN_004d3952(0);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

