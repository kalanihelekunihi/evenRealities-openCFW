
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void HciSetLeSupFeat(uint param_1,uint param_2,char param_3)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar2 = _DAT_0052ae1c;
  if (param_3 == '\0') {
    puVar1 = _DAT_0052ae1c + 1;
    *_DAT_0052ae1c = *_DAT_0052ae1c & ~param_1;
    puVar2[1] = *puVar1 & ~param_2;
  }
  else {
    puVar1 = _DAT_0052ae1c + 1;
    *_DAT_0052ae1c = param_1 | *_DAT_0052ae1c;
    puVar2[1] = param_2 | *puVar1;
  }
  return;
}

