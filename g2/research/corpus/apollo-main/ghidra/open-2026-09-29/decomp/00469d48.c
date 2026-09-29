
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
system_close_common_data_handler
          (undefined4 param_1,undefined1 *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iStack_14;
  int iStack_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_3 != 5) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0046a834,DAT_0046a830,_DAT_0046a82c,0x93,_DAT_0046a828,param_3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,_DAT_0046a838,_DAT_0046a838,param_3);
    }
    return 0xffffffff;
  }
  *_DAT_0046a83c = *param_2;
  *_DAT_0046a840 = *(undefined4 *)(param_2 + 1);
  iVar1 = FUN_0045a568();
  if ((iVar1 == 1) && (iVar1 = FUN_00443484(), iVar1 == 1)) {
    FUN_00443504(&iStack_14,&iStack_10);
    if ((iStack_10 != 0) ||
       (((((iStack_14 != 8 && (iStack_14 != 0xb)) && (iStack_14 != 5)) &&
         ((iStack_14 != 6 && (iStack_14 != 0xe0)))) && (iStack_14 != 0xffe)))) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0046a834,DAT_0046a830,_DAT_0046a82c,0xa3,_DAT_0046a844,iStack_14);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,_DAT_0046aab8,_DAT_0046aab8,iStack_14);
      }
      return 0xffffffff;
    }
    FUN_0045a8ee(0x22,0,0,100);
  }
  return 0;
}

