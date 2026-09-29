
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004e9e32(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ea7f8,DAT_004ea7f4,_DAT_004ea7f0,0x7d,_DAT_004ea7ec,param_1,param_2,
                 param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10c00000,_DAT_004ea7fc,_DAT_004ea7fc,param_1,param_2,param_3);
  }
  if ((param_1 == 0) || (8 < param_2)) {
    uVar2 = 0;
  }
  else {
    FUN_00439be4(param_2 * 0x428 + DAT_004ea7e4,param_1,0x428);
    *DAT_004ea7e8 = (short)param_3;
    uVar2 = 1;
  }
  return uVar2;
}

