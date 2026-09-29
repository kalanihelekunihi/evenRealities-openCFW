
undefined8
FUN_005d08f6(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  char *pcVar2;
  undefined4 uVar3;
  char *local_18;
  undefined4 uStack_14;
  
  local_18 = (char *)*param_1;
  pcVar2 = (char *)param_1[2];
  uVar3 = 0;
  uStack_14 = param_4;
  FUN_005d0736(&local_18,pcVar2);
  if (local_18 < pcVar2) {
    if ((*local_18 == '[') || (*local_18 == ']')) {
      local_18 = local_18 + 1;
    }
    else if (*local_18 == '{') {
      uVar3 = FUN_005d087c(&local_18,pcVar2);
    }
    else if (*local_18 == '(') {
      uVar3 = FUN_005d0794(&local_18,pcVar2);
    }
    else if (*local_18 == '<') {
      if ((local_18 + 1 < pcVar2) && (local_18[1] == '<')) {
        local_18 = local_18 + 2;
      }
      else {
        uVar3 = FUN_005d0814(&local_18,pcVar2);
      }
    }
    else if (*local_18 == '>') {
      pcVar1 = local_18 + 1;
      if ((pcVar1 < pcVar2) && (*pcVar1 == '>')) {
        local_18 = local_18 + 2;
      }
      else {
        uVar3 = 3;
        local_18 = pcVar1;
      }
    }
    else {
      if (*local_18 == '/') {
        local_18 = local_18 + 1;
      }
      for (; (((((local_18 < pcVar2 && (*local_18 != ' ')) && (*local_18 != '\r')) &&
               ((*local_18 != '\n' && (*local_18 != '\t')))) &&
              (((*local_18 != '\f' && ((*local_18 != '\0' && (*local_18 != '/')))) &&
               (*local_18 != '(')))) &&
             ((((*local_18 != ')' && (*local_18 != '<')) && (*local_18 != '>')) &&
              (((*local_18 != '[' && (*local_18 != ']')) &&
               ((*local_18 != '{' && ((*local_18 != '}' && (*local_18 != '%'))))))))));
          local_18 = local_18 + 1) {
      }
    }
  }
  if ((local_18 < pcVar2) && (local_18 == (char *)*param_1)) {
    uVar3 = 3;
  }
  if (pcVar2 < local_18) {
    local_18 = pcVar2;
  }
  param_1[3] = uVar3;
  *param_1 = local_18;
  return CONCAT44(uStack_14,local_18);
}

