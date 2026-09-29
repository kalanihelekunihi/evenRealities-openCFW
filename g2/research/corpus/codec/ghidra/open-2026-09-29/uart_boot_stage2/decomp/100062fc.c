
int gx8002_stage2_strlen(uint *param_1)

{
  uint *puVar1;
  
  puVar1 = param_1;
  if (((uint)param_1 & 3) != 0) goto LAB_1000633c;
  if ((DAT_10006348 + *param_1 & ~*param_1 & DAT_1000634c) != 0) goto LAB_1000633c;
  do {
    puVar1 = puVar1 + 1;
  } while ((DAT_10006348 + *puVar1 & ~*puVar1 & DAT_1000634c) == 0);
  if ((char)*puVar1 != '\0') {
    do {
      puVar1 = (uint *)((int)puVar1 + 1);
LAB_1000633c:
    } while ((char)*puVar1 != '\0');
    return (int)puVar1 - (int)param_1;
  }
  return (int)puVar1 - (int)param_1;
}

