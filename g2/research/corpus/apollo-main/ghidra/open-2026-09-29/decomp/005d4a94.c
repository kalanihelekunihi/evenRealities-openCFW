
undefined8 FUN_005d4a94(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (*(char *)(param_1 + 0x2d90) != '\0') {
    *(undefined1 *)(param_1 + 0x2d91) = 1;
    FUN_005d47d4(param_1,*(undefined4 *)(param_1 + 0x2dd8),*(undefined4 *)(param_1 + 0x2ddc));
    if (*(char *)(param_1 + 0x2de0) != '\0') {
      param_3 = 1;
      param_2 = *(undefined4 *)(param_1 + 0x2dc4);
      FUN_005d431e(param_1,param_1 + 8,param_1 + 0x2db8,*(undefined4 *)(param_1 + 0x2dc0),param_2,1,
                   param_4);
    }
    *(undefined1 *)(param_1 + 0x2d93) = 1;
    *(undefined1 *)(param_1 + 0x2d90) = 0;
    *(undefined1 *)(param_1 + 0x2d91) = 0;
    *(undefined1 *)(param_1 + 0x2de0) = 0;
  }
  return CONCAT44(param_3,param_2);
}

