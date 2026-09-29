
void FUN_005d0b7c(uint *param_1,undefined4 *param_2,int param_3,int *param_4)

{
  undefined4 *puVar1;
  uint uVar2;
  uint uVar3;
  int local_38;
  int local_34;
  char local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  undefined4 local_24;
  
  *param_4 = -1;
  FUN_005d0a72(param_1,&local_38);
  if (local_30 == '\x03') {
    uVar3 = *param_1;
    uVar2 = param_1[2];
    *param_1 = local_38 + 1;
    param_1[2] = local_34 - 1;
    puVar1 = param_2;
    while ((*param_1 < param_1[2] && (FUN_005d0a72(param_1,&local_2c), (char)local_24 != '\0'))) {
      if ((param_2 != (undefined4 *)0x0) && (puVar1 < param_2 + param_3 * 3)) {
        *puVar1 = local_2c;
        puVar1[1] = uStack_28;
        puVar1[2] = local_24;
      }
      puVar1 = puVar1 + 3;
    }
    *param_4 = ((int)puVar1 - (int)param_2) / 0xc;
    *param_1 = uVar3;
    param_1[2] = uVar2;
  }
  return;
}

