
undefined8 FT_Get_CMap_Format(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined4 uStack_10;
  undefined4 local_c;
  
  uStack_10 = param_3;
  if ((param_1 == (int *)0x0) || (*param_1 == 0)) {
    local_c = 0xffffffff;
  }
  else {
    piVar3 = *(int **)(*param_1 + 0x60);
    puVar2 = (undefined4 *)0x0;
    local_c = param_4;
    if (*(int *)(*piVar3 + 0x20) != 0) {
      puVar2 = (undefined4 *)(**(code **)(*piVar3 + 0x20))(piVar3,DAT_005274fc);
    }
    if (puVar2 == (undefined4 *)0x0) {
      local_c = 0xffffffff;
    }
    else {
      iVar1 = (*(code *)*puVar2)(param_1,&uStack_10);
      if (iVar1 != 0) {
        local_c = 0xffffffff;
      }
    }
  }
  return CONCAT44(uStack_10,local_c);
}

