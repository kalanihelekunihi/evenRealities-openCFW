
undefined8 FUN_004e7d20(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  piVar2 = DAT_004e8454;
  iVar5 = param_1;
  if ((*DAT_004e8454 != 0) &&
     (iVar3 = FUN_0043e2ea(*DAT_004e8454), piVar1 = DAT_004e83bc, iVar3 != 0)) {
    if (*DAT_004e83bc == 0) {
      iVar4 = FUN_0044e498(*piVar2);
      piVar1 = DAT_004e7ff4;
      iVar3 = iVar4;
      if ((param_1 == 1) && (iVar3 = *DAT_004e7ff4, iVar3 < *DAT_004e80dc + -1)) {
        *DAT_004e7ff4 = *DAT_004e7ff4 + 1;
        FUN_004e7cc0(*piVar2,iVar4 + 0x130,*DAT_004e83b8);
        FUN_004e772c(*piVar1);
      }
      else if ((param_1 == -1) && (iVar3 = *DAT_004e7ff4, 0 < iVar3)) {
        *DAT_004e7ff4 = *DAT_004e7ff4 + -1;
        FUN_004e7cc0(*piVar2,iVar4 + -0x130,*DAT_004e83b8);
        FUN_004e772c(*piVar1);
      }
      else {
        FUN_004e7b16(param_1,iVar4,iVar3);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar5 = 0x224;
        param_2 = DAT_004e8498;
        FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e849c,0x224,DAT_004e8498,*piVar1,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004e84a0,DAT_004e84a0,*piVar1);
      }
    }
  }
  return CONCAT44(param_2,iVar5);
}

