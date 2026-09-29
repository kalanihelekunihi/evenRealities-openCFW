
void FUN_00439ce0(undefined4 param_1,uint param_2,float *param_3,int *param_4,int *param_5,
                 int *param_6)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  float fVar8;
  undefined1 local_70;
  undefined1 local_6f;
  undefined1 local_6e;
  int local_6c;
  int local_68;
  int aiStack_64 [16];
  
  if (param_2 == 3) {
    piVar2 = aiStack_64 + 3;
    do {
      *piVar2 = *param_4;
      loopEnd();
      param_4 = param_4 + 1;
      piVar2 = piVar2 + 1;
    } while( true );
  }
  piVar2 = aiStack_64 + 3;
  aiStack_64[7] = 0;
  aiStack_64[8] = 0;
  VectorStoreRegister(piVar2,2,4,0);
  if ((int)(param_2 << 0x18) < 0) {
    FUN_00439e90(aiStack_64 + 9,param_4,0x3fc);
  }
  else {
    if ((param_2 & 0x7f) == 0) {
      if (param_2 != 0) {
        piVar4 = aiStack_64 + param_2 + 9;
        piVar5 = aiStack_64 + 6;
        do {
          piVar3 = piVar4 + 1;
          *piVar5 = *piVar4;
          piVar4 = piVar3;
          piVar5 = piVar5 + 1;
        } while (piVar3 != aiStack_64 + param_2 * 2 + 9);
      }
      uVar6 = FUN_00439e9c(param_3);
      uVar6 = FUN_00439efc(param_1,uVar6);
      uVar7 = FUN_00439f24(param_3);
      fVar8 = (float)FUN_00439f88(uVar6,uVar7);
      local_70 = *param_3 == fVar8;
      local_6f = param_3[1] == fVar8;
      local_6e = param_3[2] == fVar8;
      iVar1 = FUN_00439fb4(&local_70,aiStack_64);
      if (iVar1 == 0) {
        FUN_00439fe4(fVar8,param_3,piVar2,&local_6c);
        *param_6 = 1;
        param_6[1] = 2;
        *param_5 = local_6c;
        param_5[1] = local_68;
        return;
      }
      *param_6 = iVar1;
      param_6[1] = 2;
      if (0 < iVar1) {
        piVar2 = param_5;
        piVar4 = aiStack_64;
        do {
          piVar5 = piVar2 + 1;
          *piVar2 = aiStack_64[*piVar4 + 2];
          piVar2 = piVar5;
          piVar4 = piVar4 + 1;
        } while (param_5 + iVar1 != piVar5);
        piVar2 = aiStack_64;
        piVar4 = param_5 + iVar1;
        do {
          piVar5 = piVar4 + 1;
          *piVar4 = aiStack_64[*piVar2 + 5];
          piVar2 = piVar2 + 1;
          piVar4 = piVar5;
        } while (piVar5 != param_5 + iVar1 * 2);
      }
      return;
    }
    FUN_00439e90(aiStack_64 + 9,param_4,(param_2 & 0x7f) << 3);
  }
  piVar4 = aiStack_64 + 9;
  do {
    *piVar2 = *piVar4;
    loopEnd();
    piVar4 = piVar4 + 1;
    piVar2 = piVar2 + 1;
  } while( true );
}

