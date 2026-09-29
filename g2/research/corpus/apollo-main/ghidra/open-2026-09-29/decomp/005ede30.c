
undefined8 tracepoint_map_requested_file(char *param_1,int param_2,char *param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int local_20;
  char *local_1c;
  undefined4 uStack_18;
  
  local_20 = param_2;
  if (((param_1 == (char *)0x0) || (param_2 == 0)) || (param_3 == (char *)0x0)) {
    uVar2 = 0xffffffff;
  }
  else {
    local_1c = param_3;
    uStack_18 = param_4;
    cVar1 = tracepoint_role_char();
    if ((*param_1 == 'R') || (*param_1 == 'L')) {
      if ((*param_1 != cVar1) || (param_1[1] != ':')) {
        uVar2 = 0xffffffff;
        goto LAB_005edeb0;
      }
      param_1 = param_1 + 2;
    }
    local_20 = 0;
    if (*param_1 == 't') {
      local_1c = (char *)0x0;
      iVar3 = FUN_0048d874(param_1 + 1,&local_1c,10);
      if (((local_1c == (char *)0x0) || (*local_1c != '\0')) || (iVar3 == 0)) {
        uVar2 = 0xffffffff;
        goto LAB_005edeb0;
      }
    }
    else {
      iVar4 = tracepoint_resolve_file_name(param_1,&local_20);
      iVar3 = local_20;
      if ((iVar4 == 0) &&
         (iVar4 = tracepoint_parse_file_sequence(param_1,&local_20), iVar3 = local_20, iVar4 == 0))
      {
        uVar2 = 0xffffffff;
        goto LAB_005edeb0;
      }
    }
    local_20 = iVar3;
    tracepoint_format_file_path(param_2,param_3,local_20);
    uVar2 = 0;
  }
LAB_005edeb0:
  return CONCAT44(local_20,uVar2);
}

