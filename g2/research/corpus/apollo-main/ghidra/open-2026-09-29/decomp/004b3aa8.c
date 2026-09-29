
undefined4 FUN_004b3aa8(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  if (*(char *)((int)param_2 + 7) != '\0') {
    *(undefined1 *)((int)param_2 + 5) = 1;
    if (*param_2 != 0) {
      FUN_0047a49c(*param_2,*(undefined1 *)((int)param_2 + 0xb));
    }
    FUN_004b467c(0);
    if (*(char *)(DAT_004b3c8c + 0x5d) == '\x01') {
      *(undefined1 *)((int)param_2 + 9) = 1;
    }
    if (*param_2 != 0) {
      FUN_004bb098(param_1,(char)param_2[1]);
    }
  }
  return param_4;
}

