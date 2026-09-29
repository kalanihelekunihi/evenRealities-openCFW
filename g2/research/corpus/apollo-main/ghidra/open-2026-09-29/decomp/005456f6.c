
int FUN_005456f6(int param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  uint uVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  
  uVar2 = DAT_00545cec;
  uVar1 = DAT_00545ce8;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545ce0,0x12f,DAT_00545cdc);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00545ce4,DAT_00545ce4);
    }
    iVar4 = 0;
  }
  else {
    FUN_0043c0e4(DAT_00545cec,DAT_00545ce8,0);
    puVar3 = DAT_00545cf0;
    *DAT_00545cf0 = *DAT_00545cf0 & 0xffffff00 | 0x19;
    *puVar3 = *puVar3 & 0xffff00ff | 0x600;
    *puVar3 = *puVar3 & 0xffff;
    puVar3[2] = puVar3[2] & 0xffff0000 | 0x240;
    puVar3[1] = puVar3[1] & 0xffff0000 | 0x240;
    puVar3[1] = puVar3[1] & 0xffff | 0xbc0000;
    puVar3[3] = uVar1;
    puVar3[4] = uVar2;
    puVar3[5] = 0;
    puVar3[6] = 0;
    iVar4 = FUN_00498668(param_1);
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545ce0,0x146,DAT_00545cf4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00545cf8,DAT_00545cf8);
      }
      iVar4 = 0;
    }
    else {
      FUN_00498680(iVar4,puVar3);
      FUN_0043f09a(iVar4,param_2,param_3);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00545cc8,DAT_00545cc4,DAT_00545ce0,0x150,DAT_00545cfc,param_2,param_3);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00546608,DAT_00546608,param_2,param_3);
      }
    }
  }
  return iVar4;
}

