
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void als_function_37(uint param_1)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  
  if (*_DAT_004aea20 == 0) {
    iVar2 = *_DAT_004aea34;
  }
  else {
    iVar2 = *_DAT_004aea20;
  }
  uVar3 = param_1;
  if (param_1 < 0x267) {
    uVar3 = 0x266;
  }
  if (uVar3 < 0x59a) {
    if (param_1 < 0x267) {
      *_DAT_004aea38 = 0x266;
    }
    else {
      *_DAT_004aea38 = param_1;
    }
  }
  else {
    *_DAT_004aea38 = 0x59a;
  }
  puVar1 = _DAT_004aea24;
  *_DAT_004aea24 = *_DAT_004aea38;
  *_DAT_004aea3c = *puVar1;
  *DAT_004ae94c = 0;
  als_function_19(iVar2);
  return;
}

