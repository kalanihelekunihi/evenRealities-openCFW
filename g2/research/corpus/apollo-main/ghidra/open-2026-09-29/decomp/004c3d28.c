
longlong FUN_004c3d28(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004c37a8(3,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = FUN_00473940();
    FUN_004c37fe(3,param_1,0);
    iVar2 = FUN_004c377a(3);
    if (iVar2 == 0) {
      FUN_00480f0c(0xf,*DAT_004c467c);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

