
int ft_service_list_lookup(int *param_1,int param_2)

{
  int iVar1;
  
  if ((param_1 != (int *)0x0) && (param_2 != 0)) {
    for (; *param_1 != 0; param_1 = param_1 + 2) {
      iVar1 = FUN_0046cacc(*param_1,param_2);
      if (iVar1 == 0) {
        return param_1[1];
      }
    }
  }
  return 0;
}

