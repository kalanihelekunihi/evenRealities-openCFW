
void FUN_005eaa96(char *param_1)

{
  int iVar1;
  
  iVar1 = DAT_005eb28c;
  if (((param_1 != (char *)0x0) && (*param_1 != '\0')) && (*(int *)(DAT_005eb28c + 4) != 0)) {
    *(char *)(DAT_005eb28c + 0x28c) = param_1[1];
    if (param_1[1] == '\0') {
      FUN_0044ea04(*(undefined4 *)(iVar1 + 4),*(undefined4 *)(param_1 + 4),0);
      FUN_005ea926(*(undefined4 *)(param_1 + 4));
    }
    else {
      FUN_005ea992();
    }
  }
  return;
}

