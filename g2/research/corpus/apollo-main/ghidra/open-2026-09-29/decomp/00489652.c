
undefined1 FUN_00489652(char *param_1,uint param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (param_2 == DAT_004897f8) {
    if (*param_1 == '\0') {
      *param_1 = '\x01';
      uVar1 = 1;
    }
    else if (*param_1 == '\0') {
      *param_1 = '\0';
    }
    else if (*param_1 == '\x02') {
      *param_1 = '\0';
      uVar1 = 1;
    }
  }
  if (*param_1 == '\x01') {
    if (param_2 == 0x20) {
      *param_1 = '\x02';
    }
    uVar1 = 1;
  }
  return uVar1;
}

