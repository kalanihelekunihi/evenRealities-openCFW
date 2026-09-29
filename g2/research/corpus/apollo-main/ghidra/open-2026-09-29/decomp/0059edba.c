
undefined4 FUN_0059edba(byte *param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  byte *pbVar4;
  
  pbVar4 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = (uint)*param_1;
    pbVar4 = (byte *)0xb3;
    param_2 = DAT_0059f470;
    FUN_0043d574(4,DAT_0059f414,DAT_0059f410,DAT_0059f474,0xb3,DAT_0059f470,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0059f478,DAT_0059f478,*param_1,pbVar4,param_2,param_3);
  }
  bVar1 = *param_1;
  if (bVar1 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059f414,DAT_0059f410,DAT_0059f474,0xb6,DAT_0059f47c,param_1[4]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0059f480,DAT_0059f480,param_1[4]);
    }
    bVar1 = param_1[4];
    if (bVar1 == 1) {
      uVar3 = FUN_00596b0c(1,param_1 + 4,0x14);
    }
    else {
      if (bVar1 != 0) {
        if (bVar1 == 3) {
          uVar3 = FUN_00596b0c(2,param_1 + 4,0x14);
          return uVar3;
        }
        if (bVar1 < 3) {
          uVar3 = FUN_00596b0c(4,param_1 + 4,0x14);
          return uVar3;
        }
        if (bVar1 == 4) {
          uVar3 = FUN_00596b0c(3,param_1 + 4,0x14);
          return uVar3;
        }
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0059f414,DAT_0059f410,DAT_0059f474,0xc1,DAT_0059f484,param_1[4]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0059f488,DAT_0059f488,param_1[4]);
      }
      uVar3 = 0xffffffff;
    }
  }
  else if (bVar1 == 2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059f414,DAT_0059f410,DAT_0059f474,0xc5,DAT_0059f48c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0059f490,DAT_0059f490);
    }
    uVar3 = FUN_00596b0c(5,param_1 + 4,0x850);
  }
  else if (bVar1 == 0xff) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059f414,DAT_0059f410,DAT_0059f474,200,DAT_0059f494);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0059f498,DAT_0059f498);
    }
    uVar3 = FUN_00596b0c(6,0,0);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0059f414,DAT_0059f410,DAT_0059f474,0xcb,DAT_0059f49c,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__translate_unknown_command_id__d_0059f4a0,
                          PTR_s__translate_unknown_command_id__d_0059f4a0,*param_1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

