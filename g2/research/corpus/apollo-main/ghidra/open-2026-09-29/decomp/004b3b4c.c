
undefined4 FUN_004b3b4c(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*param_2 == 0) {
    if ((*(short *)(param_1 + 0xe) == 0) &&
       (iVar1 = FUN_004751c8(param_1 + 6,DAT_004b45ac,8), iVar1 == 0)) {
      if (*(char *)(DAT_004b3c8c + 0x74) != '\0') {
        *(undefined1 *)(DAT_004b3c8c + 0x6c) = 1;
        return param_4;
      }
    }
    else {
      iVar1 = FUN_0047add4(*(undefined2 *)(param_1 + 0xe),param_1 + 6);
      *param_2 = iVar1;
      if (*param_2 != 0) {
        *(undefined1 *)(DAT_004b3c8c + 0x74) = 0;
      }
    }
  }
  FUN_004b36b2(param_2);
  return param_4;
}

