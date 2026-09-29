
void FUN_0056395c(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint in_fpscr;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  piVar1 = DAT_00563f3c;
  iVar2 = *DAT_00563f3c;
  *(undefined1 *)(iVar2 + 0x2e5) = 1;
  *(undefined4 *)(iVar2 + 0x2fc) = 0;
  *(undefined4 *)(iVar2 + 0x2f8) = 0;
  *(undefined1 *)(iVar2 + 0x2e8) = 0;
  *(undefined1 *)(iVar2 + 0x2e9) = 0;
  if (*(float *)(iVar2 + 0x300) < 0.0) {
    fVar4 = -*(float *)(iVar2 + 0x300);
    fVar5 = *(float *)(iVar2 + 0x2f4);
    fVar6 = fVar4 / fVar5;
    fVar7 = (float)VectorSignedToFloat((int)fVar6,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    if (0.0 <= fVar6) {
      uVar3 = -(uint)(fVar6 < fVar7);
    }
    else {
      uVar3 = (uint)(fVar7 < fVar6);
    }
    fVar6 = (float)VectorSignedToFloat((int)fVar6 + uVar3,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3
                                      );
    *(float *)(iVar2 + 0x300) = (fVar6 * fVar5 - fVar4) + fVar5;
  }
  *(undefined4 *)(iVar2 + 0x304) = *(undefined4 *)(*piVar1 + 0x300);
  return;
}

