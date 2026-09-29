
undefined4 FUN_0053a454(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_38;
  int aiStack_34 [7];
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x01') {
        FUN_00480f0c(*(undefined4 *)(param_1 + uVar3 * 0xc),*DAT_0053a66c);
        FUN_00480fd6(*(undefined4 *)(param_1 + uVar3 * 0xc),
                     *(char *)(uVar3 * 0xc + param_1 + 5) == '\x01');
      }
      else if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x02') {
        FUN_00480f0c(*(undefined4 *)(param_1 + uVar3 * 0xc),
                     *DAT_0053a664 & 0xffffff3f | (*(byte *)(uVar3 * 0xc + param_1 + 6) & 3) << 6);
        if ((*(char *)(uVar3 * 0xc + param_1 + 6) != '\0') &&
           (*(int *)(uVar3 * 0xc + param_1 + 8) != 0)) {
          local_38 = *(uint *)(param_1 + uVar3 * 0xc);
          FUN_0048949c(aiStack_34,0x1c);
          aiStack_34[local_38 >> 5] = 1 << (local_38 & 0x1f);
          FUN_004812f6(0,1,aiStack_34);
          FUN_00481468(0,aiStack_34);
          FUN_0048162c(0,local_38,*(undefined4 *)(uVar3 * 0xc + param_1 + 8),0);
          FUN_004810b0(0,1,&local_38);
          iVar1 = DAT_0053a668;
          FUN_0053a430((int)*(short *)(DAT_0053a668 + (*(uint *)(param_1 + uVar3 * 0xc) >> 5) * 2),4
                      );
          FUN_0053a414((int)*(short *)(iVar1 + (*(uint *)(param_1 + uVar3 * 0xc) >> 5) * 2));
        }
      }
      else if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x04') {
        FUN_00480f0c(*(undefined4 *)(param_1 + uVar3 * 0xc),*DAT_0053a660);
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

