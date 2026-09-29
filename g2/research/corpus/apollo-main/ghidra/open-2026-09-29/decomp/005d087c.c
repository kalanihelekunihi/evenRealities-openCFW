
undefined8 FUN_005d087c(undefined4 *param_1,char *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char *local_18;
  
  iVar2 = 0;
  iVar3 = 0;
  local_18 = (char *)*param_1;
  do {
    if ((param_2 <= local_18) || (iVar3 != 0)) goto LAB_005d08d0;
    cVar1 = *local_18;
    if (cVar1 == '%') {
      FUN_005d071c(&local_18,param_2);
    }
    else if (cVar1 == '(') {
      iVar3 = FUN_005d0794(&local_18,param_2);
    }
    else if (cVar1 == '<') {
      iVar3 = FUN_005d0814(&local_18,param_2);
    }
    else if (cVar1 == '{') {
      iVar2 = iVar2 + 1;
    }
    else if ((cVar1 == '}') && (iVar2 = iVar2 + -1, iVar2 == 0)) {
      local_18 = local_18 + 1;
LAB_005d08d0:
      if (iVar2 != 0) {
        iVar3 = 3;
      }
      *param_1 = local_18;
      return CONCAT44(local_18,iVar3);
    }
    local_18 = local_18 + 1;
  } while( true );
}

