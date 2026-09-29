
undefined1 DmConnRole(byte param_1)

{
  undefined1 uVar1;
  
  if ((param_1 == 0) || (3 < param_1)) {
    uVar1 = 0xff;
  }
  else {
    uVar1 = *(undefined1 *)((uint)param_1 * 0x30 + DAT_004b7430 + -0x17);
  }
  return uVar1;
}

