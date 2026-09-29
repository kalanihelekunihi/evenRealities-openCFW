
undefined4 FUN_004f509a(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  quicklist_lock_storage();
  FUN_0043c0e4(DAT_004f5c3c,0x2e50,0);
  FUN_0043c0e4(DAT_004f5c40,0x288,0);
  if (param_1 != '\0') {
    *DAT_004f5c44 = 0;
  }
  quicklist_unlock_storage();
  return param_4;
}

