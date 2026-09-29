
undefined4
am_devices_mspi_jbd4010_read_dieId
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_1a;
  undefined1 uStack_19;
  undefined1 uStack_18;
  undefined1 uStack_17;
  byte bStack_16;
  undefined1 uStack_15;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(&uStack_20,0xc,0);
  iVar1 = jbd4010_read_die_response(0x81,&uStack_20,0xc,DAT_00593910);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00593900,DAT_005938fc,DAT_00593918,0x26e,DAT_00593920,uStack_20,uStack_1f,
                   uStack_1e,uStack_1d,uStack_1c,uStack_1b,uStack_1a,uStack_19,uStack_18,uStack_17,
                   bStack_16,uStack_15);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output((bStack_16 & 0xf) << 0x16 | 0xc000000,DAT_00593924,DAT_00593924,uStack_20,
                          uStack_1f,uStack_1e,uStack_1d,uStack_1c,uStack_1b,uStack_1a,uStack_19,
                          uStack_18,uStack_17,bStack_16,uStack_15);
    }
    if (param_1 != 0) {
      FUN_00439be4(param_1,&uStack_20,0xc);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_00593918,0x268,DAT_00593914,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0059391c,DAT_0059391c,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

