
undefined1 ring_address_is_unset_004a26e8(char *param_1)

{
  undefined1 uVar1;
  
  if (param_1 == (char *)0x0) {
    uVar1 = 1;
  }
  else if ((((*param_1 == -1) && (param_1[1] == -1)) && (param_1[2] == -1)) &&
          (((param_1[3] == -1 && (param_1[4] == -1)) && (param_1[5] == -1)))) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

