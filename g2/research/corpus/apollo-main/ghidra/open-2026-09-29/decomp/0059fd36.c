
undefined4 FUN_0059fd36(byte param_1,undefined4 param_2,char *param_3)

{
  if (param_1 != 0) {
    if (param_1 == 2) {
      *(undefined4 *)(param_3 + 4) = DAT_0059ffd4;
      *(undefined4 *)(param_3 + 8) = DAT_0059ffd8;
    }
    else if (param_1 < 2) {
      if (*param_3 == '\0') {
        FUN_0059fca2();
      }
      else {
        FUN_0059fbac(*param_3);
      }
    }
  }
  return 0;
}

