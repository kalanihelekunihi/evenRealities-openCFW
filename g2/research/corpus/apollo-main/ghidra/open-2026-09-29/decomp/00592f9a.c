
undefined4
am_devices_mspi_jbd4010_read_chipId
          (undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 uStack_34;
  undefined1 local_33;
  undefined1 local_32;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&uStack_34,0x24,0);
  iVar1 = jbd4010_read_response(0x9f,&uStack_34,4);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00593900,DAT_005938fc,DAT_005938f8,0x259,DAT_00593908,
                   CONCAT11(local_33,local_32));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0059390c,DAT_0059390c,CONCAT11(local_33,local_32));
    }
    if (param_1 != (undefined2 *)0x0) {
      *param_1 = CONCAT11(local_33,local_32);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00593900,DAT_005938fc,DAT_005938f8,0x256,DAT_005938f4,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00593904,DAT_00593904,iVar1);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

