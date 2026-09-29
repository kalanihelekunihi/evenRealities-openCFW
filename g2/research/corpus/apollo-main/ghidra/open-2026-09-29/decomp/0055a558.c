
undefined4
PB_RxHealthSingleData(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 local_38;
  undefined4 local_34;
  undefined8 local_30;
  double local_28;
  double local_20;
  undefined4 local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_38,DAT_0055abc8,0x14);
    local_34 = CONCAT22(local_34._2_2_,1);
    APP_errorFaultHandler(&local_38);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_34 = DAT_0055abcc;
      local_38 = 0x6f;
      FUN_0043d574(1,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055abd0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055abd4);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = (uint)param_2[0x15];
      local_18 = *(undefined4 *)(param_2 + 0x10);
      local_20 = (double)*(float *)(param_2 + 0xc);
      local_28 = (double)*(float *)(param_2 + 8);
      local_30 = (double)CONCAT44(*(undefined4 *)(param_2 + 4),(uint)*param_2);
      local_34 = DAT_0055abd8;
      local_38 = 0x74;
      FUN_0043d574(4,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055abd0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_20 = (double)(ulonglong)CONCAT14(param_2[0x15],*(undefined4 *)(param_2 + 0x10));
      local_28 = (double)*(float *)(param_2 + 0xc);
      local_30 = (double)*(float *)(param_2 + 8);
      local_38 = *(undefined4 *)(param_2 + 4);
      compress_log_output(0x11800000,DAT_0055ad58,DAT_0055ad58,*param_2);
    }
    uVar3 = FUN_005598cc(param_2);
    if ((uVar3 & 0xff) == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_30 = (double)CONCAT44(local_30._4_4_,(uint)*param_2);
        local_34 = DAT_0055ad64;
        local_38 = 0x7d;
        FUN_0043d574(3,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055abd0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_0055af00,DAT_0055af00,*param_2);
      }
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_30 = (double)(CONCAT44(local_30._4_4_,uVar3) & 0xffffffff000000ff);
        local_34 = DAT_0055ad5c;
        local_38 = 0x79;
        FUN_0043d574(1,PTR_s_pb_health_0055ab9c,DAT_0055abb8,DAT_0055abd0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0055ad60,DAT_0055ad60,uVar3 & 0xff);
      }
      uVar2 = 1;
    }
  }
  return uVar2;
}

