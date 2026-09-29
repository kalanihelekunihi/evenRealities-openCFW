
void FUN_0800afcc(uint *param_1)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar2 = DAT_0800b01c;
  do {
    puVar1 = puVar2;
    puVar2 = (uint *)*puVar1;
  } while (puVar2 < param_1);
  if ((uint *)(puVar1[1] + (int)puVar1) == param_1) {
    puVar1[1] = puVar1[1] + param_1[1];
    param_1 = puVar1;
  }
  if (param_1[1] + (int)param_1 == *puVar1) {
    if (puVar2 == (uint *)*DAT_0800b020) {
      *param_1 = (uint)*DAT_0800b020;
    }
    else {
      param_1[1] = param_1[1] + puVar2[1];
      *param_1 = *(uint *)*puVar1;
    }
  }
  else {
    *param_1 = (uint)puVar2;
  }
  if (puVar1 != param_1) {
    *puVar1 = (uint)param_1;
  }
  return;
}

