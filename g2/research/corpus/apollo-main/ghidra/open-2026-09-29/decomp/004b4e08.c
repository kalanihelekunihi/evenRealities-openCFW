
void attL2cCtrlCback(undefined2 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = attCcbByConnId((char)*param_1);
  if (*(char *)(iVar2 + 0xe) != '\0') {
    if (*(char *)(param_1 + 1) == '\x01') {
      *(byte *)(iVar2 + 2) = *(byte *)(iVar2 + 2) | 2;
    }
    else {
      *(byte *)(iVar2 + 2) = *(byte *)(iVar2 + 2) & 0xfd;
      iVar1 = DAT_004b51d0;
      (**(code **)(*(int *)(DAT_004b51d0 + 0x40) + 4))(param_1);
      if (-1 < (int)((uint)*(byte *)(iVar2 + 2) << 0x1e)) {
        (**(code **)(*(int *)(iVar1 + 0x3c) + 4))(param_1);
      }
    }
  }
  return;
}

