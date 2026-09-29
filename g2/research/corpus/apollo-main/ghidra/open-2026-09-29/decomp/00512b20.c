
undefined4 FUN_00512b20(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  byte local_14 [4];
  undefined4 uStack_10;
  
  if (param_1 == (uint *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    local_14[0] = 0;
    uStack_10 = param_4;
    iVar2 = FUN_0055fc38(DAT_00512c60,0x101,local_14,1);
    if (iVar2 == DAT_00512c1c) {
      if ((local_14[0] == 0) || (local_14[0] == 0xff)) {
        local_14[0] = 0x13;
      }
      *param_1 = (uint)local_14[0];
      uVar1 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,DAT_00512c7c,0x51d,DAT_00512c78,iVar2
                    );
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00512c80,DAT_00512c80,iVar2);
      }
      uVar1 = 0xfffffffe;
    }
  }
  return uVar1;
}

