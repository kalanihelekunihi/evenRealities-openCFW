
void FUN_005eaa54(char *param_1,undefined4 *param_2,char *param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_005eb28c;
  if ((param_2 != (undefined4 *)0x0) && (param_3 != (char *)0x0)) {
    if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
      if (*(int *)(DAT_005eb28c + 4) == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = FUN_0044e498(*(undefined4 *)(DAT_005eb28c + 4));
      }
      *param_2 = uVar2;
      *param_3 = *(char *)(iVar1 + 0x28c);
    }
    else {
      *param_2 = *(undefined4 *)(param_1 + 4);
      *param_3 = param_1[1];
    }
  }
  return;
}

