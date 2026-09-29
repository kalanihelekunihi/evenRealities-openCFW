
undefined4 FUN_00490678(char *param_1)

{
  bool bVar1;
  
  bVar1 = false;
  while( true ) {
    if (bVar1) {
      return 0;
    }
    if (*param_1 != '\0') break;
    bVar1 = true;
  }
  return 1;
}

