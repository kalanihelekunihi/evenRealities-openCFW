
undefined8 FUN_0041fe06(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_00420874;
  local_10 = param_3;
  uStack_c = param_4;
  am_hal_mspi_interrupt_status_get(*DAT_00420874,&local_10,0);
  am_hal_mspi_interrupt_clear(*puVar1,local_10);
  am_hal_mspi_interrupt_service(*puVar1,local_10);
  return CONCAT44(uStack_c,local_10);
}

