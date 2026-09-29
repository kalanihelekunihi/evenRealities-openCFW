
undefined4 FUN_00508a4e(undefined1 *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined1 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else if (*DAT_00508a8c == '\0') {
    uVar1 = 0xfffffffe;
  }
  else {
    *param_1 = *DAT_00508a88;
    uVar1 = 0;
  }
  return uVar1;
}

