
undefined4 appSlaveLegAdvRestart(int param_1)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 2) == '(') {
    if (*(char *)(DAT_004b2dc8 + 0x75) != '\0') {
      *(undefined1 *)(DAT_004b2dc8 + 0x75) = 0;
      return unaff_r7;
    }
  }
  else if (*(char *)(param_1 + 2) == '\'') {
    if (*(char *)(DAT_004b2dc8 + 0x75) != '\0') {
      *(undefined1 *)(DAT_004b2dc8 + 0x75) = 0;
      return unaff_r7;
    }
    *(undefined1 *)(DAT_004b2dc8 + 0x57) = 3;
  }
  if (*(char *)(DAT_004b2dc8 + 0x57) == '\x03') {
    *(undefined1 *)(DAT_004b2dc8 + 0x57) = 0;
    appSlaveLegAdvStart();
  }
  return unaff_r7;
}

