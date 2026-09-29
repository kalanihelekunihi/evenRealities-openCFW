
void KwsStragegyInsertKwsActivation(float param_1,float param_2,float param_3,uint param_4)

{
  uint *puVar1;
  uint uVar2;
  float *pfVar3;
  int iVar4;
  float in_vr0;
  
  puVar1 = puRam10208a08;
  uVar2 = *puRam10208a08;
  pfVar3 = (float *)(puRam10208a08 + 1);
  iVar4 = 0;
  while( true ) {
    if ((int)uVar2 <= iVar4) {
      if (uVar2 < 8) {
        pfVar3 = (float *)(puRam10208a08 + uVar2 * 5);
        pfVar3[1] = param_1;
        pfVar3[2] = param_2;
        *pfVar3 = in_vr0;
        pfVar3[4] = param_3;
        puVar1[(uVar2 + 1) * 5] = param_4;
        *puVar1 = uVar2 + 1;
      }
      else {
        gx8002_printf(uRam10208a0c);
      }
      return;
    }
    if ((pfVar3[1] == param_2) && (*pfVar3 == param_1)) break;
    iVar4 = iVar4 + 1;
    pfVar3 = pfVar3 + 5;
  }
  if (in_vr0 <= (float)puRam10208a08[iVar4 * 5]) {
    return;
  }
  puRam10208a08[iVar4 * 5] = (uint)in_vr0;
  return;
}

