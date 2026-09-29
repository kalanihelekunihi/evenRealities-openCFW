
int raccess_get_rule_type_from_rule_index(undefined4 param_1,uint param_2)

{
  int iVar1;
  
  if (param_2 < 9) {
    iVar1 = (int)*(char *)(DAT_00528714 + param_2 * 8 + 4);
  }
  else {
    iVar1 = -2;
  }
  return iVar1;
}

