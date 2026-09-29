
undefined1 settings_role_head_up_profile(uint param_1)

{
  undefined1 uVar1;
  char cVar2;
  
  if (2 < param_1) {
    param_1 = 2;
  }
  cVar2 = FUN_0045a570();
  if (cVar2 == '\x01') {
    uVar1 = *(undefined1 *)(DAT_0046c730 + param_1);
  }
  else {
    uVar1 = *(undefined1 *)(DAT_0046c734 + param_1);
  }
  return uVar1;
}

