
undefined4 gx8002_max_score(int *param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  float fVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  float fVar16;
  float fVar17;
  int iStack_44;
  
  iVar1 = iRam10208878;
  gx8002_memset(iRam10208878,0,2);
  func_0x10025608(param_1[4],*(undefined4 *)(*param_1 + 0x44));
  iVar3 = LvpCTCModelGetSnpuOutBuffer(param_1[4]);
  iVar10 = *(int *)(iVar1 + 4);
  *(undefined1 *)((int)param_1 + 0xd) = 0;
  uVar2 = uRam1020887c;
  fVar7 = 0.0;
  iVar13 = 0;
  iVar10 = (iVar10 % 10) * 8 + iVar1 + 8;
  for (uVar12 = 0; uVar12 < *(uint *)(iVar1 + 0x58); uVar12 = uVar12 + 1) {
    iVar5 = *(int *)(iVar1 + 0x5c) + iVar13;
    uVar11 = *(uint *)(iVar5 + 0x54) & 1;
    if (uVar11 == param_2) {
      iVar15 = (int)(*(float *)(iVar3 + uVar12 * 4) * fVar7);
      gx8002_bionic_run(param_1,iVar5,0,param_2,iVar15);
      iVar5 = *(int *)(iVar1 + 0x5c) + iVar13;
      iVar8 = *(int *)(iVar5 + 0x4c);
      if (*(int *)(iVar5 + 0x54) != 0) {
        fVar16 = (float)iVar8;
        fVar17 = fVar16;
        gx8002_bunkws_offset(param_1);
        iVar15 = (int)(fVar17 + fVar16);
      }
      iVar5 = uVar12 * 4;
      if ((iVar8 < iStack_44) &&
         (iVar6 = *(int *)(iVar1 + 0x5c) + iVar13, uVar11 == (*(uint *)(iVar6 + 0x54) & 1))) {
        *(int *)(iVar1 + 0x60) = iStack_44;
        *(undefined4 *)(iVar10 + iVar5) = 1;
        iVar14 = 0;
        uVar11 = (uint)*(byte *)(iVar1 + uVar12);
        iVar4 = 10;
        do {
          uVar9 = uVar11 + *(int *)(iVar5 + iVar1 + 8 + iVar14 * 8);
          uVar11 = uVar9 & 0xff;
          iVar14 = iVar14 + 1;
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
        *(char *)(iVar1 + uVar12) = (char)uVar9;
        if (uVar11 == 1) {
          KwsStragegyInsertKwsActivation(uVar12,*(undefined4 *)(iVar6 + 0x50),0,0,iVar15);
          iVar5 = *(int *)(iVar1 + 0x5c) + iVar13;
          gx8002_printf(uVar2,param_1[2],iVar5,*(undefined4 *)(iVar5 + 0x50),iVar8,
                        *(int *)(iVar1 + 0x60),*(int *)(iVar1 + 0x60) - iVar8);
          *(undefined4 *)(iVar1 + 0x60) = 0;
          if (*(int *)(*(int *)(iVar1 + 0x5c) + iVar13 + 0x54) != 0) {
            gx8002_bunkws_offset_clear();
          }
        }
      }
      else {
        *(undefined4 *)(iVar10 + iVar5) = 0;
      }
    }
    iVar13 = iVar13 + 0x58;
  }
  return 0;
}

