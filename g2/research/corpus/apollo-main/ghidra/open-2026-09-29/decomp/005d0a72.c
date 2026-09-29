
char * FUN_005d0a72(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,char *param_4)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  char *pcVar4;
  char *local_18;
  
  *(undefined1 *)(param_2 + 2) = 0;
  *param_2 = 0;
  param_2[1] = 0;
  local_18 = param_4;
  FUN_005d0a68(param_1);
  local_18 = (char *)*param_1;
  pcVar4 = (char *)param_1[2];
  if (local_18 < pcVar4) {
    cVar1 = *local_18;
    if (cVar1 == '(') {
      *(undefined1 *)(param_2 + 2) = 2;
      *param_2 = local_18;
      iVar3 = FUN_005d0794(&local_18,pcVar4);
      if (iVar3 == 0) {
        param_2[1] = local_18;
      }
    }
    else {
      if (cVar1 == '[') {
        *(undefined1 *)(param_2 + 2) = 3;
        iVar3 = 1;
        *param_2 = local_18;
        local_18 = local_18 + 1;
        *param_1 = local_18;
        FUN_005d0a68(param_1);
        local_18 = (char *)*param_1;
        do {
          if ((pcVar4 <= local_18) || (param_1[3] != 0)) goto LAB_005d0b68;
          if (*local_18 == '[') {
            iVar3 = iVar3 + 1;
          }
          else if ((*local_18 == ']') && (iVar3 = iVar3 + -1, iVar3 < 1)) {
            local_18 = local_18 + 1;
            param_2[1] = local_18;
            goto LAB_005d0b68;
          }
          *param_1 = local_18;
          FUN_005d08f6(param_1);
          FUN_005d0a68(param_1);
          local_18 = (char *)*param_1;
        } while( true );
      }
      if (cVar1 == '{') {
        *(undefined1 *)(param_2 + 2) = 3;
        *param_2 = local_18;
        iVar3 = FUN_005d087c(&local_18,pcVar4);
        if (iVar3 == 0) {
          param_2[1] = local_18;
        }
      }
      else {
        *param_2 = local_18;
        if (*local_18 == '/') {
          uVar2 = 4;
        }
        else {
          uVar2 = 1;
        }
        *(undefined1 *)(param_2 + 2) = uVar2;
        FUN_005d08f6(param_1);
        local_18 = (char *)*param_1;
        if (param_1[3] == 0) {
          param_2[1] = local_18;
        }
      }
    }
LAB_005d0b68:
    if (param_2[1] == 0) {
      *param_2 = 0;
      *(undefined1 *)(param_2 + 2) = 0;
    }
    *param_1 = local_18;
  }
  return local_18;
}

