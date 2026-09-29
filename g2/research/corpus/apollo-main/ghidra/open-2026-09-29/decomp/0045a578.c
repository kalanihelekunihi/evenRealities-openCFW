
undefined4 FUN_0045a578(void)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int local_24;
  int local_20 [5];
  
  FUN_00480f0c(0x9c,*DAT_0045ade0);
  FUN_0043c0e4(local_20,0x14,0);
  bVar1 = true;
  iVar4 = 0;
  while( true ) {
    if (4 < iVar4) {
      if (bVar1) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0045b100,DAT_0045b0fc,DAT_0045b0f8,0x98,DAT_0045b110,local_20[0]);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0045b114,DAT_0045b114,local_20[0]);
        }
        if (local_20[0] == 1) {
          *DAT_0045b0f4 = 2;
          uVar3 = 2;
        }
        else {
          *DAT_0045b0f4 = 1;
          uVar3 = 1;
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b0f8,0x91,DAT_0045b108);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0045b10c,DAT_0045b10c);
        }
        uVar3 = 3;
      }
      return uVar3;
    }
    iVar2 = FUN_00480f8a(0x9c,0,&local_24);
    if (iVar2 != 0) break;
    local_20[iVar4] = local_24;
    if ((0 < iVar4) && (local_20[iVar4] != local_20[0])) {
      bVar1 = false;
    }
    if (iVar4 < 4) {
      FUN_004910f4(5);
    }
    iVar4 = iVar4 + 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_0045b100,DAT_0045b0fc,DAT_0045b0f8,0x7f,DAT_0045ade4,iVar4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4400000,DAT_0045b104,DAT_0045b104,iVar4);
  }
  return 3;
}

