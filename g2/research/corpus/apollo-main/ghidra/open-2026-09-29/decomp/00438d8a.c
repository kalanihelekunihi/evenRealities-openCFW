
void FUN_00438d8a(longlong *param_1,int param_2,undefined2 *param_3,int param_4)

{
  longlong lVar1;
  longlong lVar2;
  longlong lVar3;
  short *psVar4;
  uint uVar5;
  short *psVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = 0;
  if (0 < param_4 * 5) {
    lVar2 = *param_1;
    lVar3 = param_1[1];
    do {
      uVar5 = iVar7 + ((uint)(iVar7 >> 2) >> 0x1d);
      psVar4 = (short *)(DAT_004396a8 + (iVar7 - (uVar5 & 0xfffffff8)) * 0x14);
      psVar6 = (short *)(param_2 + ((int)uVar5 >> 3) * 2);
      iVar8 = (int)*psVar6 * (int)psVar4[9] +
              (int)psVar6[-1] * (int)psVar4[8] +
              (int)psVar6[-2] * (int)psVar4[7] +
              (int)psVar6[-3] * (int)psVar4[6] +
              (int)psVar6[-4] * (int)psVar4[5] +
              (int)psVar6[-5] * (int)psVar4[4] +
              (int)psVar6[-6] * (int)psVar4[3] +
              (int)psVar6[-7] * (int)psVar4[2] +
              (int)psVar6[-9] * (int)*psVar4 + (int)psVar6[-8] * (int)psVar4[1];
      lVar1 = (longlong)DAT_00438fa4 * (longlong)iVar8;
      lVar2 = lVar2 + lVar1;
      uVar5 = (uint)lVar2 >> 0x1e | (int)((ulonglong)lVar2 >> 0x20) * 4;
      lVar2 = ((longlong)DAT_00438fa8 * (longlong)iVar8 + lVar3) -
              (longlong)DAT_00438fa0 * (longlong)(int)uVar5;
      lVar3 = lVar1 - (longlong)DAT_00438fac * (longlong)(int)uVar5;
      *param_3 = (short)(uVar5 + 0x8000 >> 0x10);
      iVar7 = iVar7 + 5;
      param_3 = param_3 + 1;
    } while (iVar7 < param_4 * 5);
    *param_1 = lVar2;
    param_1[1] = lVar3;
  }
  return;
}

