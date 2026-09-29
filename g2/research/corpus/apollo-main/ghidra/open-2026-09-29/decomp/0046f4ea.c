
undefined8 FUN_0046f4ea(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_00470014;
  local_10 = param_3;
  uStack_c = param_4;
  FUN_004c2392(*DAT_00470014,&local_10,0);
  am_hal_mspi_interrupt_clear(*puVar1,local_10);
  FUN_004c240e(*puVar1,local_10);
  return CONCAT44(uStack_c,local_10);
}

