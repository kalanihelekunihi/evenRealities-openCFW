
undefined4 am_devices_mspi_jbd4010_init(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    *DAT_005932fc = param_1;
    *DAT_00593300 = param_2;
    am_devices_mspi_init(DAT_005932f8,param_3,DAT_005931fc,DAT_00593304);
    uVar1 = jbd4010_vtable_init(1);
  }
  return uVar1;
}

