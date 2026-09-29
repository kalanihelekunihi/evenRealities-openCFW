
undefined8 hardware_readiness_gate_42bf54(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((*DAT_0042bfd8 == 0) && (*DAT_0042bfdc == 0)) {
    iVar1 = FUN_0041bf84(0x1d);
    if (iVar1 == 0) {
      iVar1 = FUN_0041ca2c(DAT_0042bfa4,&stack0xfffffff0);
      if (iVar1 == 0) {
        iVar1 = delay_status_change(0x9c4,DAT_0042c030,1,0);
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

