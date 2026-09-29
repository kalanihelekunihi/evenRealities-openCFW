
void FT_Outline_Transform(int param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  
  if ((param_1 != 0) && (param_2 != 0)) {
    uVar1 = *(uint *)(param_1 + 4);
    uVar2 = uVar1 + *(short *)(param_1 + 2) * 8;
    for (; uVar1 < uVar2; uVar1 = uVar1 + 8) {
      FT_Vector_Transform(uVar1,param_2);
    }
  }
  return;
}

