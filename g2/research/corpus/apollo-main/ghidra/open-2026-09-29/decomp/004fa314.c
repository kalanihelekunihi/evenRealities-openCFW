
undefined8 FUN_004fa314(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  short *psVar2;
  int iVar3;
  
  piVar1 = DAT_004fac60;
  if ((*DAT_004fac60 != 0) && (iVar3 = FUN_0043e2ea(*DAT_004fac60), iVar3 != 0)) {
    FUN_004fb1a4(*piVar1,1);
    FUN_004f5596();
    FUN_004f9484();
    FUN_0043f66c(*piVar1);
    psVar2 = DAT_004fac4c;
    piVar1 = DAT_004fa3f0;
    if (*DAT_004fac4c == 0) {
      if ((*DAT_004fa3f0 != 0) && (iVar3 = FUN_0043e2ea(*DAT_004fa3f0), iVar3 == 1)) {
        *DAT_004fa3f4 = 0;
        *DAT_004faa2c = 0xffffffff;
        FUN_0043dfa4(*piVar1,1);
        FUN_00441488(*piVar1,0xff,0);
        FUN_0043f09a(*piVar1,0,0);
        FUN_0043f4c0(*piVar1,0x240,0x120);
      }
    }
    else {
      *DAT_004faa2c = 0;
      FUN_004f9afc(0);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x10bc;
      param_3 = DAT_004faf18;
      FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004faf1c,0x10bc,DAT_004faf18,*psVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004fb078,DAT_004fb078,*psVar2);
    }
  }
  return CONCAT44(param_3,param_2);
}

