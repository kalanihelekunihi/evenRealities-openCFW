
longlong FUN_004c43ec(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 local_10;
  
  iVar3 = FUN_004c37a8(6,param_1);
  local_10 = param_3;
  if (iVar3 != 0) {
    local_10 = FUN_00473940();
    FUN_004c37fe(6,param_1,0);
    iVar3 = FUN_004c377a(6);
    if (iVar3 == 0) {
      *DAT_004c4698 = 0;
      puVar2 = DAT_004c469c;
      FUN_00539a10(*DAT_004c469c);
      FUN_00539944(*puVar2);
      *puVar2 = 0;
      if (*DAT_004c4654 == '\0') {
        FUN_004c3e9a(0x35);
      }
      else {
        FUN_004c3d28(0x35);
      }
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

