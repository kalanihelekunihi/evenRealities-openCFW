
int cJSON_GetArraySize(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  iVar1 = 0;
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else {
    for (puVar2 = *(undefined4 **)(param_1 + 8); puVar2 != (undefined4 *)0x0;
        puVar2 = (undefined4 *)*puVar2) {
      iVar1 = iVar1 + 1;
    }
  }
  return iVar1;
}

