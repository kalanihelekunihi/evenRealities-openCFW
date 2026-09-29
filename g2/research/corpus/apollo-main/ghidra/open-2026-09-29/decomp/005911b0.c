
void FUN_005911b0(byte *param_1,float *param_2)

{
  float *pfVar1;
  byte *pbVar2;
  undefined2 uVar3;
  int iVar4;
  float local_18;
  
  if ((int)((*param_1 + 1) * *(int *)(DAT_005915a8 + (uint)param_1[2] * 4)) < 1) {
    return;
  }
  local_18 = *param_2;
  pfVar1 = (float *)(param_1 + *(int *)(param_1 + 0x4a4) * 4 + 0x4ac);
  pbVar2 = param_1 + *(int *)(param_1 + 0x4a0) * 2 + 0x4ac;
  do {
    if (((uint)local_18 & 0x7f800000) != 0) {
      local_18 = (float)((int)local_18 + 0x7800000);
    }
    iVar4 = (int)local_18;
    if (iVar4 < DAT_005915c4) {
      uVar3 = (undefined2)DAT_005915c0;
    }
    else {
      if (0x7ffe < iVar4) {
        iVar4 = 0x7fff;
      }
      uVar3 = (undefined2)iVar4;
    }
    *(undefined2 *)pbVar2 = uVar3;
    *pfVar1 = local_18;
    loopEnd();
    pfVar1 = pfVar1 + 1;
    pbVar2 = pbVar2 + 2;
  } while( true );
}

