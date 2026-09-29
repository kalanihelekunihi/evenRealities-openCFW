
undefined8
FUN_005d0cc2(undefined4 *param_1,char *param_2,int param_3,int param_4,undefined4 param_5)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  int *piVar5;
  char *local_30;
  int iStack_2c;
  int local_28;
  
  local_30 = (char *)*param_1;
  iVar3 = 0;
  if (local_30 < param_2) {
    cVar4 = '\0';
    if (*local_30 == '[') {
      cVar4 = ']';
    }
    else if (*local_30 == '{') {
      cVar4 = '}';
    }
    iStack_2c = param_3;
    local_28 = param_3;
    if (cVar4 != '\0') {
      local_30 = local_30 + 1;
    }
    do {
      if ((param_2 <= local_30) ||
         (FUN_005d0736(&local_30,param_2), pcVar1 = local_30, param_2 <= local_30)) break;
      if (*local_30 == cVar4) {
        local_30 = local_30 + 1;
        break;
      }
      if ((param_4 != 0) && (local_28 <= iVar3)) break;
      if (param_4 == 0) {
        piVar5 = &iStack_2c;
      }
      else {
        piVar5 = (int *)(param_4 + iVar3 * 4);
      }
      iVar2 = FUN_005d01de(&local_30,param_2,param_5);
      *piVar5 = iVar2;
      if (pcVar1 == local_30) {
        iVar3 = -1;
        break;
      }
      iVar3 = iVar3 + 1;
    } while (cVar4 != '\0');
  }
  *param_1 = local_30;
  return CONCAT44(local_30,iVar3);
}

