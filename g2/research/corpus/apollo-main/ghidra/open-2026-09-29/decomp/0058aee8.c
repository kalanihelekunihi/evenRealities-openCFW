
void semantic_ensure_range(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = *(uint *)(DAT_0058b530 + 0x5194);
  uVar1 = *(uint *)(DAT_0058b530 + 0x5190);
  if (uVar2 < 5) {
    iVar3 = 0;
  }
  else {
    iVar3 = uVar2 - 5;
  }
  *param_1 = iVar3;
  *param_2 = uVar2 + 8;
  if (uVar1 <= *param_2) {
    if (uVar1 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = uVar1 - 1;
    }
    *param_2 = uVar1;
  }
  return;
}

