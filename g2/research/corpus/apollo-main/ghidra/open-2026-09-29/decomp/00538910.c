
undefined8 _thread_ble_production_msg_crc_check(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  char cVar2;
  ushort uVar3;
  byte bVar4;
  
  bVar4 = 0;
  if (param_1 == 0) {
    bVar4 = 0;
  }
  else {
    cVar2 = '\0';
    for (uVar3 = 0; uVar3 < (ushort)(*(byte *)(param_1 + 3) + 4); uVar3 = uVar3 + 1) {
      cVar2 = cVar2 + *(char *)(param_1 + (uint)uVar3);
    }
    if (cVar2 == *(char *)((uint)*(byte *)(param_1 + 3) + param_1 + 4)) {
      bVar4 = 1;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x131;
        FUN_0043d574(1,DAT_00538b54,DAT_00538b50,PTR_s__thread_ble_production_msg_crc_c_00538bf0,
                     0x131,PTR_s_ble_production_msg_crc_check_fai_00538bec);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__task_ble_production_ble_product_00538bf4,
                            PTR_s__task_ble_production_ble_product_00538bf4);
      }
    }
  }
  return CONCAT44(param_3,(uint)bVar4);
}

