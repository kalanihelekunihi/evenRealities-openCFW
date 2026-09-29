
void attDmConnCback(undefined2 *param_1)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  
  iVar3 = attCcbByConnId((char)*param_1);
  if (*(char *)(param_1 + 1) == '\'') {
    *(undefined2 *)(iVar3 + 0xc) = param_1[3];
    *(char *)(iVar3 + 0xe) = (char)*param_1;
    for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
      *(undefined2 *)(iVar3 + (uint)bVar2 * 4) = 0xf7;
      *(undefined1 *)(iVar3 + (uint)bVar2 * 4 + 2) = 0;
    }
    *(undefined4 *)(iVar3 + 0x10) = 0;
  }
  iVar1 = DAT_004b51d0;
  if (*(char *)(iVar3 + 0xe) != '\0') {
    (**(code **)(*(int *)(DAT_004b51d0 + 0x40) + 0xc))(iVar3,param_1);
    (**(code **)(*(int *)(iVar1 + 0x3c) + 0xc))(iVar3,param_1);
    if ((*(char *)(param_1 + 1) == '(') &&
       (*(undefined1 *)(iVar3 + 0xe) = 0, *(int *)(iVar3 + 0x10) != 0)) {
      WsfBufFree(*(undefined4 *)(iVar3 + 0x10));
    }
  }
  iVar3 = DAT_004b51d0;
  if (*(int *)(DAT_004b51d0 + 0x50) != 0) {
    (**(code **)(DAT_004b51d0 + 0x50))(param_1);
  }
  if (*(int *)(iVar3 + 0x5c) != 0) {
    (**(code **)(iVar3 + 0x5c))(param_1);
  }
  return;
}

