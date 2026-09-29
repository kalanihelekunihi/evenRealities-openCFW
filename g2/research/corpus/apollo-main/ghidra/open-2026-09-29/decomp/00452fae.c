
undefined4 FUN_00452fae(char *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (char *)0x0) {
    uVar1 = 0;
  }
  else if ((*param_1 == '\x01') || (*param_1 == '\x03')) {
    uVar1 = *(undefined4 *)(param_1 + 0x70);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

