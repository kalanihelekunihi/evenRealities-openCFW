
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void semantic_set_magnetic_vector(undefined4 *param_1)

{
  undefined4 *puVar1;
  
  puVar1 = _DAT_004a657c;
  *_DAT_004a657c = *param_1;
  puVar1[1] = param_1[1];
  puVar1[2] = param_1[2];
  return;
}

