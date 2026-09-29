
void FUN_1000e94c(int param_1,short *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  short *psVar5;
  int iVar6;
  float fVar7;
  float fVar8;
  short local_1c;
  
  fVar3 = 0.0;
  FUN_100100a4();
  if (0 < *(int *)(param_1 + 4)) {
    iVar6 = 0;
    fVar8 = 0.0;
    do {
      fVar7 = (float)(int)param_2[iVar6] * fVar3;
      FUN_10011af4();
      FUN_1000fc58();
      FUN_10012398();
      fVar2 = DAT_1000ea64;
      fVar1 = DAT_1000ea60;
      if (fVar8 <= fVar7) {
        fVar8 = fVar7;
      }
      iVar6 = iVar6 + 1;
      iVar4 = *(int *)(param_1 + 4);
    } while (iVar6 < iVar4);
    if (fVar8 - DAT_1000ea60 < 0.0) {
      fVar8 = 0.0;
    }
    else {
      fVar8 = 0.0 / (fVar8 - DAT_1000ea60);
    }
    if (0 < iVar4) {
      psVar5 = param_2 + iVar4;
      do {
        while (fVar7 = (float)(int)*param_2 * fVar3, fVar1 < fVar7) {
          fVar7 = (fVar7 - fVar1) * fVar8 + fVar1;
LAB_1000e9f6:
          local_1c = (short)(int)fVar7;
          *param_2 = local_1c;
          param_2 = param_2 + 1;
          if (psVar5 == param_2) {
            return;
          }
        }
        if (fVar7 < fVar2) {
          fVar7 = (fVar7 + fVar1) * fVar8 - fVar1;
          goto LAB_1000e9f6;
        }
        local_1c = (short)(int)fVar7;
        *param_2 = local_1c;
        param_2 = param_2 + 1;
        if (psVar5 == param_2) {
          return;
        }
      } while( true );
    }
  }
  return;
}

