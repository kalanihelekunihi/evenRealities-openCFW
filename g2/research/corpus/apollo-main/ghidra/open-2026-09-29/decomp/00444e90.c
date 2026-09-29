
undefined8 _RPC_SystemOtaStatusSync(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint local_18;
  undefined1 local_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  uint local_10;
  undefined4 uStack_c;
  
  local_14 = (undefined1)param_2;
  uStack_13 = (undefined1)((uint)param_2 >> 8);
  uStack_12 = (undefined1)((uint)param_2 >> 0x10);
  uStack_11 = (undefined1)((uint)param_2 >> 0x18);
  local_18 = param_1;
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_10 = param_1 & 0xff;
    local_14 = (undefined1)DAT_004455bc;
    uStack_13 = (undefined1)((uint)DAT_004455bc >> 8);
    uStack_12 = (undefined1)((uint)DAT_004455bc >> 0x10);
    uStack_11 = (undefined1)((uint)DAT_004455bc >> 0x18);
    local_18 = 0x332;
    FUN_0043d574(4,DAT_004455b0,DAT_004455ac,DAT_004455c0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004455c4,DAT_004455c4,param_1 & 0xff);
  }
  if (*DAT_004455b8 == '\0') {
    local_18 = *DAT_004455c8;
    uVar2 = DAT_004455c8[1];
    local_14 = (undefined1)uVar2;
    uStack_13 = (undefined1)(uVar2 >> 8);
    uStack_12 = (undefined1)(uVar2 >> 0x10);
    uStack_11 = (undefined1)(uVar2 >> 0x18);
    local_14 = FUN_0045a568();
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      uStack_13 = 2;
    }
    else {
      uStack_13 = 1;
    }
    uStack_12 = (undefined1)param_1;
    FUN_00464d1c(0x103,&local_18,8,0);
  }
  return CONCAT17(uStack_11,CONCAT16(uStack_12,CONCAT15(uStack_13,CONCAT14(local_14,local_18))));
}

