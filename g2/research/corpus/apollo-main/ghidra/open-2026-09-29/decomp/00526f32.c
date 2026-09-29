
undefined8 FT_Get_First_Char(int param_1,uint *param_2,uint *param_3,undefined4 param_4)

{
  uint uVar1;
  uint *puVar2;
  int iVar3;
  uint *local_18;
  undefined4 uStack_14;
  
  puVar2 = (uint *)0x0;
  uVar1 = 0;
  local_18 = param_3;
  if (((param_1 != 0) && (*(int *)(param_1 + 0x5c) != 0)) && (*(int *)(param_1 + 0x10) != 0)) {
    iVar3 = *(int *)(param_1 + 0x5c);
    local_18 = param_2;
    uStack_14 = param_4;
    do {
      uVar1 = (**(code **)(*(int *)(iVar3 + 0xc) + 0x10))(iVar3,&local_18);
    } while (*(uint *)(param_1 + 0x10) <= uVar1);
    puVar2 = local_18;
    if (uVar1 == 0) {
      puVar2 = (uint *)0x0;
    }
  }
  if (param_3 != (uint *)0x0) {
    *param_3 = uVar1;
  }
  return CONCAT44(local_18,puVar2);
}

