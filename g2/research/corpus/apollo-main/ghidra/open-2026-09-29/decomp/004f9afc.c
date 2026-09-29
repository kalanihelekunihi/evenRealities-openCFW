
void FUN_004f9afc(int param_1)

{
  int *piVar1;
  int iVar2;
  int local_1c;
  undefined4 local_18;
  undefined4 local_14;
  int local_10;
  
  piVar1 = DAT_004fa3f0;
  if (((*DAT_004fa3f0 != 0) && (-1 < param_1)) && (param_1 < (int)(uint)*DAT_004fa04c)) {
    *DAT_004fa3f4 = 2;
    FUN_004f6fc4(param_1,&local_10,&local_1c,&local_14,&local_18);
    iVar2 = FUN_0044e498(*DAT_004f9f0c);
    local_1c = local_1c - iVar2;
    FUN_0043dfa4(*piVar1,1);
    FUN_00441488(*piVar1,0xff,0);
    FUN_0043f09a(*piVar1,local_10 + 0xc,local_1c + 8);
    FUN_0043f4c0(*piVar1,local_14,local_18);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f9bd8,DAT_004fa400,DAT_004fa3fc,0xf4f,DAT_004fa3f8,param_1,local_10,
                   local_1c,local_14,local_18);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x11400000,DAT_004fa704,DAT_004fa704,param_1,local_10,local_1c,local_14,
                          local_18);
    }
  }
  return;
}

