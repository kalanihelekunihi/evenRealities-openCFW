
undefined8 FUN_00442524(int param_1,undefined4 param_2,undefined4 param_3,undefined2 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    if (*DAT_00442cd4 <= iVar2) {
      iVar2 = param_1;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar2 = 0x97;
        param_2 = DAT_00442cfc;
        FUN_0043d574(2,DAT_00442cf4,DAT_00442cf0,DAT_00442d10,0x97,DAT_00442cfc,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00442d00,DAT_00442d00,param_1);
      }
LAB_004425a4:
      return CONCAT44(param_2,iVar2);
    }
    if ((*(int *)(DAT_00442cd8 + iVar2 * 0x10) == param_1) &&
       (*(int *)(iVar2 * 0x10 + DAT_00442cd8 + 4) != 0)) {
      (**(code **)(DAT_00442cd8 + iVar2 * 0x10 + 4))(param_4);
      iVar2 = param_1;
      goto LAB_004425a4;
    }
    iVar2 = iVar2 + 1;
  } while( true );
}

