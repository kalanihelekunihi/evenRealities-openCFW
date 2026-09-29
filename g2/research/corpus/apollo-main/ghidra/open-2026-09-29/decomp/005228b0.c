
void FUN_005228b0(float param_1,float param_2)

{
  bool bVar1;
  float fVar2;
  undefined4 *puVar3;
  float extraout_s1;
  
  puVar3 = (undefined4 *)FUN_00514aec(2);
  fVar2 = DAT_00522a20;
  if (puVar3 != (undefined4 *)0x0) {
    *puVar3 = 0x174;
    bVar1 = fVar2 <= -param_1;
    puVar3[1] = -param_2;
    puVar3[2] = 0x168;
    puVar3[3] = -param_1;
    fVar2 = extraout_s1;
    if (bVar1) {
      fVar2 = DAT_00522a20;
    }
    if (!bVar1 || (!bVar1 || -param_2 < fVar2)) {
      FUN_00514846(0x118,0x80000000);
      return;
    }
  }
  return;
}

