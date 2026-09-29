
/* WARNING: Instruction at (ram,0x00599766) overlaps instruction at (ram,0x00599764)
    */

void FUN_00599714(int param_1,int param_2,undefined4 param_3,float *param_4)

{
  uint uVar1;
  float *pfVar2;
  uint uVar3;
  float *pfVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  float local_268 [130];
  
  iVar5 = *(int *)(DAT_00599b7c + param_1 * 0x1c + param_2 * 4);
  if (iVar5 < 0x20) {
    uVar3 = 0x20 - iVar5 * (0x20 / iVar5);
    uVar1 = iVar5 - uVar3;
    if (0 < (int)uVar3) {
      pfVar4 = local_268;
      if ((uVar3 & 3) != 0) {
        do {
          fVar6 = *param_4;
          pfVar4[3] = fVar6;
          pfVar4[2] = fVar6;
          pfVar4[1] = fVar6;
          *pfVar4 = fVar6;
          pfVar4 = pfVar4 + 4;
          param_4 = param_4 + 1;
          loopEnd();
        } while( true );
      }
      if (uVar3 >> 2 != 0) {
        do {
          fVar6 = *param_4;
          pfVar4[3] = fVar6;
          pfVar4[2] = fVar6;
          pfVar4[1] = fVar6;
          *pfVar4 = fVar6;
          fVar6 = param_4[1];
          pfVar4[7] = fVar6;
          pfVar4[6] = fVar6;
          pfVar4[5] = fVar6;
          pfVar4[4] = fVar6;
          fVar6 = param_4[2];
          pfVar4[0xb] = fVar6;
          pfVar4[10] = fVar6;
          pfVar4[9] = fVar6;
          pfVar4[8] = fVar6;
          fVar6 = param_4[3];
          pfVar4[0xf] = fVar6;
          pfVar4[0xe] = fVar6;
          pfVar4[0xd] = fVar6;
          pfVar4[0xc] = fVar6;
          pfVar4 = pfVar4 + 0x10;
          param_4 = param_4 + 4;
          loopEnd();
        } while( true );
      }
    }
  }
  else {
    uVar3 = 0;
    uVar1 = 0x40 - iVar5;
  }
  pfVar4 = local_268 + uVar3 * 4;
  param_4 = param_4 + uVar3;
  if ((int)uVar3 < (int)(uVar1 + uVar3)) {
    if ((uVar1 & 3) != 0) {
      do {
        fVar6 = *param_4;
        pfVar4[1] = fVar6;
        *pfVar4 = fVar6;
        pfVar4 = pfVar4 + 2;
        param_4 = param_4 + 1;
        loopEnd();
      } while( true );
    }
    if (uVar1 >> 2 != 0) {
      do {
        fVar6 = *param_4;
        pfVar4[1] = fVar6;
        *pfVar4 = fVar6;
        fVar6 = param_4[1];
        pfVar4[3] = fVar6;
        pfVar4[2] = fVar6;
        fVar6 = param_4[2];
        pfVar4[5] = fVar6;
        pfVar4[4] = fVar6;
        fVar6 = param_4[3];
        pfVar4[7] = fVar6;
        pfVar4[6] = fVar6;
        pfVar4 = pfVar4 + 8;
        param_4 = param_4 + 4;
        loopEnd();
      } while( true );
    }
  }
  FUN_00439be4(pfVar4 + uVar1 * 2,param_4 + uVar1,((iVar5 - uVar3) - uVar1) * 4);
  pfVar2 = *(float **)(DAT_00599b80 + param_2 * 4);
  pfVar4 = local_268;
  fVar6 = local_268[0];
  do {
    fVar7 = pfVar4[1] * 0.25;
    *pfVar4 = (local_268[0] * 0.25 + fVar6 * 0.5 + fVar7) * *pfVar2;
    local_268[0] = pfVar4[2];
    pfVar4[1] = (fVar6 * 0.25 + pfVar4[1] * 0.5 + local_268[0] * 0.25) * pfVar2[1];
    fVar6 = pfVar4[3];
    pfVar4[2] = (fVar7 + local_268[0] * 0.5 + fVar6 * 0.25) * pfVar2[2];
    pfVar2 = pfVar2 + 3;
    pfVar4 = pfVar4 + 3;
    loopEnd();
  } while( true );
}

