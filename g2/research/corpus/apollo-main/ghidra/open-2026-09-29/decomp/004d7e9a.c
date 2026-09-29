
int cJSON_ParseWithOpts(int param_1,int *param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int local_40;
  uint local_3c;
  uint local_38;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  FUN_0048949c(&local_40,0x1c);
  piVar1 = DAT_004d7f8c;
  iVar4 = 0;
  *DAT_004d7f8c = 0;
  piVar1[1] = 0;
  if (param_1 != 0) {
    local_40 = param_1;
    iVar4 = FUN_0044a43c(param_1);
    local_3c = iVar4 + 1;
    local_38 = 0;
    local_30 = *DAT_004d7f94;
    uStack_2c = DAT_004d7f94[1];
    uStack_28 = DAT_004d7f94[2];
    iVar4 = cJSON_New_Item();
    if (iVar4 != 0) {
      skip_utf8_bom(&local_40);
      uVar2 = buffer_skip_whitespace();
      iVar3 = parse_value(iVar4,uVar2);
      if ((iVar3 != 0) &&
         ((param_3 == 0 ||
          ((buffer_skip_whitespace(&local_40), local_38 < local_3c &&
           (*(char *)(local_40 + local_38) == '\0')))))) {
        if (param_2 == (int *)0x0) {
          return iVar4;
        }
        *param_2 = local_40 + local_38;
        return iVar4;
      }
    }
  }
  if (iVar4 != 0) {
    cJSON_Delete(iVar4);
  }
  if (param_1 != 0) {
    if ((local_3c <= local_38) && (local_38 = 0, local_3c != 0)) {
      local_38 = local_3c - 1;
    }
    if (param_2 != (int *)0x0) {
      *param_2 = param_1 + local_38;
    }
    *piVar1 = param_1;
    piVar1[1] = local_38;
  }
  return 0;
}

