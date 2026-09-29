
undefined4 FUN_0047627e(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  int local_14;
  undefined4 uStack_10;
  
  uVar2 = DAT_00476490;
  uVar1 = DAT_00476474;
  uStack_10 = in_r3;
  iVar3 = FUN_004cfa62(DAT_00476474,DAT_00476490);
  if (iVar3 != 0) {
    FUN_004cfa58(uVar1,uVar2);
    iVar3 = FUN_004cfa62(uVar1,uVar2);
    if (iVar3 != 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_004764ac,0x7f,DAT_004764a8,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004764b0,DAT_004764b0,iVar3);
      }
      return 9;
    }
  }
  iVar3 = FUN_00475fe8();
  if (iVar3 != 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00476464,DAT_00476460,DAT_004764ac,0x86,DAT_004764b4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004764b8);
    }
    FUN_004761d2();
  }
  *DAT_004764bc = 1;
  uVar2 = DAT_004764c0;
  local_14 = 0;
  FUN_004cfa94(uVar1,DAT_004764c0,DAT_004764c4,0x103);
  FUN_004cfb40(uVar1,uVar2,&local_14,4);
  local_14 = local_14 + 1;
  FUN_004cfc24(uVar1,uVar2);
  FUN_004cfb7c(uVar1,uVar2,&local_14,4);
  FUN_004cfad0(uVar1,uVar2);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00476464,DAT_00476460,DAT_004764ac,0x9a,DAT_004764c8,local_14);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__file_system_boot_count___d_004764cc,
                        PTR_s__file_system_boot_count___d_004764cc,local_14);
  }
  return 0;
}

