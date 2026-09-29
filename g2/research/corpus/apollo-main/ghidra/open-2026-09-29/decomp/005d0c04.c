
undefined8 FUN_005d0c04(undefined4 *param_1,char *param_2,int param_3,int param_4)

{
  char *pcVar1;
  undefined2 extraout_var;
  int iVar2;
  char cVar3;
  int *piVar4;
  char *local_30;
  int iStack_2c;
  int iStack_28;
  
  local_30 = (char *)*param_1;
  iVar2 = 0;
  if (local_30 < param_2) {
    cVar3 = '\0';
    if (*local_30 == '[') {
      cVar3 = ']';
    }
    else if (*local_30 == '{') {
      cVar3 = '}';
    }
    iStack_2c = param_3;
    iStack_28 = param_4;
    if (cVar3 != '\0') {
      local_30 = local_30 + 1;
    }
    do {
      if ((param_2 <= local_30) ||
         (FUN_005d0736(&local_30,param_2), pcVar1 = local_30, param_2 <= local_30)) break;
      if (*local_30 == cVar3) {
        local_30 = local_30 + 1;
        break;
      }
      if ((param_4 != 0) && (param_3 <= iVar2)) break;
      if (param_4 == 0) {
        piVar4 = &iStack_2c;
      }
      else {
        piVar4 = (int *)(param_4 + iVar2 * 2);
      }
      FUN_005d01de(&local_30,param_2,0);
      *(undefined2 *)piVar4 = extraout_var;
      if (pcVar1 == local_30) {
        iVar2 = -1;
        break;
      }
      iVar2 = iVar2 + 1;
    } while (cVar3 != '\0');
  }
  *param_1 = local_30;
  return CONCAT44(local_30,iVar2);
}

