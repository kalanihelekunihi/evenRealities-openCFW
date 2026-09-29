
longlong FUN_004c4016(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = FUN_004c37a8(4,param_1);
  local_10 = param_3;
  if (iVar2 != 0) {
    local_10 = FUN_00473940();
    FUN_004c37fe(4,param_1,0);
    iVar2 = FUN_004c377a(4);
    if (iVar2 == 0) {
      FUN_004d391e(0);
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

