
int ft_list_get_node_at(int *param_1,int param_2)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    for (iVar1 = *param_1; iVar1 != 0; iVar1 = *(int *)(iVar1 + 4)) {
      if (param_2 == 0) {
        return iVar1;
      }
      param_2 = param_2 + -1;
    }
  }
  return 0;
}

