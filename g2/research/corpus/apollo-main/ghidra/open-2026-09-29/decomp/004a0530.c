
undefined8 _bleMasterGetCB(ushort *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  piVar1 = DAT_004a06b8;
  *DAT_004a06b8 = DAT_004a06bc + (uint)*param_1 * 0x30 + -0x30;
  piVar2 = DAT_004a1218;
  *(char *)(*DAT_004a1218 + 0x55) = (char)*param_1;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_4 = *piVar1;
    param_2 = 0x221;
    param_3 = DAT_004a06c0;
    FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a06c4,0x221,DAT_004a06c0,param_4);
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_004a0594;
  }
  compress_log_output(0x10400000,DAT_004a06c8,DAT_004a06c8,*piVar1,param_2,param_3,param_4);
LAB_004a0594:
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0x222;
    param_3 = DAT_004a06cc;
    FUN_0043d574(4,DAT_004a0fd0,DAT_004a0fcc,DAT_004a06c4,0x222,DAT_004a06cc,
                 *(undefined1 *)(*piVar2 + 0x55));
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004a06d0,DAT_004a06d0,*(undefined1 *)(*piVar2 + 0x55));
  }
  return CONCAT44(param_3,param_2);
}

