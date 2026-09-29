
undefined8
am_devices_mspi_jbd4010_term
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_005932f8;
  uStack_10 = param_3;
  uStack_c = param_4;
  if (*DAT_005932f8 != 0) {
    FUN_004c2392(*DAT_005932f8,&uStack_10,0);
    am_hal_mspi_interrupt_clear(*piVar1,uStack_10);
    FUN_004c240e(*piVar1,uStack_10);
  }
  return CONCAT44(uStack_c,uStack_10);
}

