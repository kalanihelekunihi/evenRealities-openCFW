
void FUN_004198fa(uint *param_1)

{
  uint *puVar1;
  
  for (puVar1 = DAT_00419964; *puVar1 < param_1; puVar1 = (uint *)*puVar1) {
  }
  if ((uint *)((int)puVar1 + puVar1[1]) == param_1) {
    puVar1[1] = param_1[1] + puVar1[1];
    param_1 = puVar1;
  }
  if ((int)param_1 + param_1[1] == *puVar1) {
    if (*puVar1 == *DAT_00419958) {
      *param_1 = *DAT_00419958;
    }
    else {
      param_1[1] = *(int *)(*puVar1 + 4) + param_1[1];
      *param_1 = *(uint *)*puVar1;
    }
  }
  else {
    *param_1 = *puVar1;
  }
  if (puVar1 != param_1) {
    *puVar1 = (uint)param_1;
  }
  return;
}

