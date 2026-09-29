
undefined8 FUN_00420e08(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00421010;
  iVar2 = am_hal_mspi_disable(*DAT_00421010);
  if (iVar2 == 0) {
    iVar2 = am_hal_mspi_device_configure(*puVar1,param_1);
    if (iVar2 == 0) {
      iVar2 = am_hal_mspi_enable(*puVar1);
      if (iVar2 == 0) {
        FUN_0041fadc(*(undefined4 *)*DAT_004210a0,*(undefined1 *)(param_1 + 8));
        uVar3 = 0;
      }
      else {
        param_2 = 0x59a;
        elog_output(2,DAT_00421034,DAT_00421030,DAT_00421098,0x59a,DAT_0042109c,param_4);
        uVar3 = 1;
      }
    }
    else {
      param_2 = 0x592;
      elog_output(2,DAT_00421034,DAT_00421030,DAT_00421098,0x592,DAT_0042109c,param_4);
      uVar3 = 1;
    }
  }
  else {
    param_2 = 0x58a;
    elog_output(2,DAT_00421034,DAT_00421030,DAT_00421098,0x58a,DAT_00421094,param_4);
    uVar3 = 1;
  }
  return CONCAT44(param_2,uVar3);
}

