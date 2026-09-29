
undefined8
FT_Stream_ReadUShort(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  undefined4 uStack_18;
  
  puVar2 = &uStack_18;
  uStack_18 = param_4;
  uVar3 = 0;
  *param_2 = 0;
  if (param_1[2] + 1U < (uint)param_1[1]) {
    if (param_1[5] == 0) {
      puVar2 = (undefined4 *)(*param_1 + param_1[2]);
    }
    else {
      iVar1 = (*(code *)param_1[5])(param_1,param_1[2],puVar2,2);
      if (iVar1 != 2) goto LAB_00528ba0;
    }
    if (puVar2 != (undefined4 *)0x0) {
      uVar3 = (uint)CONCAT11(*(undefined1 *)puVar2,*(undefined1 *)((int)puVar2 + 1));
    }
    param_1[2] = param_1[2] + 2;
  }
  else {
LAB_00528ba0:
    *param_2 = 0x55;
    uVar3 = 0;
  }
  return CONCAT44(uStack_18,uVar3);
}

