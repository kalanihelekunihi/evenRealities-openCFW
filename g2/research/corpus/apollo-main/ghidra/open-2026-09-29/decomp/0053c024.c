
undefined8
bq27427_status_update(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar1 = bq27427_read_flags(0);
  if ((uVar1 == 0) || ((uVar1 & 0xff) == 0xff)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x2a9;
      FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c27c,0x2a9,DAT_0053c278,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053c280,DAT_0053c280);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (-1 < (int)uVar1) {
      uVar3 = bq27427_read_soc();
      iVar4 = bq27427_read_temperature();
      uVar5 = bq27427_read_battery_voltage();
      bq27427_read_nom_capacity();
      bq27427_read_avail_capacity();
      bq27427_read_rem_capacity();
      bq27427_read_full_capacity();
      uVar6 = bq27427_read_ai();
      bq27427_read_ap();
      bq27427_read_int_temp();
      bq27427_read_rem_cap_unfl();
      bq27427_read_rem_cap_fil();
      bq27427_read_full_cap_unfl();
      bq27427_read_full_cap_fil();
      bq27427_read_soc_unfl();
      iVar2 = DAT_0053c284;
      *(undefined4 *)(DAT_0053c284 + 4) = uVar3;
      *(undefined4 *)(iVar2 + 8) = uVar5;
      *(undefined4 *)(iVar2 + 0xc) = uVar6;
      *(int *)(iVar2 + 0x10) = iVar4 * 10;
    }
    uVar3 = 0;
  }
  return CONCAT44(param_2,uVar3);
}

