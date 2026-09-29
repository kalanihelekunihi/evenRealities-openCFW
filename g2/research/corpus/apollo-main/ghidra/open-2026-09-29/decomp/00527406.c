
void ft_module_get_service(int *param_1,undefined4 param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  
  iVar1 = 0;
  if (param_1 != (int *)0x0) {
    if (*(int *)(*param_1 + 0x20) != 0) {
      iVar1 = (**(code **)(*param_1 + 0x20))
                        (param_1,param_2,*(code **)(*param_1 + 0x20),param_4,param_4);
    }
    if ((param_3 != '\0') && (iVar1 == 0)) {
      puVar2 = (undefined4 *)(param_1[1] + 0x14);
      puVar3 = puVar2 + *(int *)(param_1[1] + 0x10);
      while ((puVar2 < puVar3 &&
             ((((int *)*puVar2 == param_1 || (*(int *)(*(int *)*puVar2 + 0x20) == 0)) ||
              (iVar1 = (**(code **)(*(int *)*puVar2 + 0x20))(*puVar2,param_2), iVar1 == 0))))) {
        puVar2 = puVar2 + 1;
      }
    }
  }
  return;
}

