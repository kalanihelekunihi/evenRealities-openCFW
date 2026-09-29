
undefined8 spotmgr_temperature_init_42ac54(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((*DAT_0042acec == 0) && (*DAT_0042acf0 == 0)) {
    iVar1 = FUN_0041bf84(0x1d);
    if (iVar1 == 0) {
      iVar1 = FUN_0041ca2c(DAT_0042acb8,&stack0xfffffff0);
      if (iVar1 == 0) {
        iVar1 = delay_status_change(0x9c4,DAT_0042ad3c,1,0);
        if (iVar1 == 0) {
          uVar2 = 0;
        }
        else {
          uVar2 = 4;
        }
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(unaff_r5,uVar2);
}

