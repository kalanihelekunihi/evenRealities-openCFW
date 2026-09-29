
undefined4 dmConnUpdActL2cUpdateCnf(int param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 0x11) != '\0') {
    *(undefined1 *)(param_1 + 0x11) = 0;
    if (*(short *)(param_2 + 4) != 0) {
      dmConnUpdateCback(param_1,(char)*(undefined2 *)(param_2 + 4));
    }
  }
  return unaff_r7;
}

