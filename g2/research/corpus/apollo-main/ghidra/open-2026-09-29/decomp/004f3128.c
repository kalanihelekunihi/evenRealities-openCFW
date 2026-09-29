
undefined8 FUN_004f3128(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  piVar2 = DAT_004f33d0;
  piVar1 = DAT_004f33b4;
  if ((*DAT_004f33d0 != 0) && (*DAT_004f33c0 == 1)) {
    if (*DAT_004f33b4 == 1) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x690;
        param_3 = DAT_004f3408;
        FUN_0043d574(3,DAT_004f33ec,DAT_004f33e8,DAT_004f3414,0x690,DAT_004f3408,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004f3410,DAT_004f3410);
      }
      FUN_00463e1c(*piVar2,1);
      *piVar2 = 0;
      *piVar1 = 0;
      *DAT_004f33b8 = 0;
      FUN_004f0e18(*DAT_004f3374);
      FUN_004f2b30(*DAT_004f33f4);
      *DAT_004f33bc = 1;
      *DAT_004f33dc = 600;
    }
  }
  return CONCAT44(param_3,param_2);
}

