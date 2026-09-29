
undefined4 touch_eeprom_5738_initialize_adapter(undefined4 *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_1c;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined4 local_14;
  
  iVar1 = touch_platform_156c_record_init(DAT_00008a74);
  if (iVar1 == 0) {
    local_1c = *param_1;
    local_18 = *(undefined1 *)(param_1 + 1);
    local_17 = *(undefined1 *)((int)param_1 + 5);
    local_16 = *(undefined1 *)((int)param_1 + 6);
    local_15 = *(undefined1 *)((int)param_1 + 7);
    local_14 = param_1[2];
    uVar2 = touch_eeprom_568c_initialize(&local_1c,param_2,DAT_00008a74);
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

