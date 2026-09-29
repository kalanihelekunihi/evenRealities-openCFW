
/* WARNING: Control flow encountered bad instruction data */

undefined4 FUN_1000e384(undefined4 param_1,undefined4 *param_2,uint param_3)

{
  int iVar1;
  undefined4 *puVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined4 *puVar7;
  uint uVar8;
  int iVar9;
  undefined4 *puVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  
  if (param_3 < 0xc4) {
    FUN_10009934(PTR_s__ImcraStateInit_Error__At_least_s_1000e77c,param_3,0xc4);
  }
  else {
    param_2[2] = 16000;
    param_2[3] = 0x200;
    param_2[4] = 0x200;
    param_2[6] = 0x200;
    param_2[7] = 0x101;
    param_2[0x12] = DAT_1000e718;
    param_2[0x13] = DAT_1000e71c;
    param_2[0x14] = DAT_1000e720;
    param_2[0x15] = 0;
    param_2[0x16] = DAT_1000e724;
    param_2[0x17] = DAT_1000e728;
    param_2[0x18] = DAT_1000e72c;
    param_2[0x19] = DAT_1000e730;
    uVar5 = 0;
    param_2[5] = 0x100;
    param_2[8] = 0;
    FUN_100100a4();
    param_2[0x1a] = 8;
    *param_2 = uVar5;
    param_2[0x1b] = 4;
    param_2[0x1c] = 2;
    param_2[0x1d] = 0;
    param_2[0x2f] = 0;
    iVar1 = FUN_1000e314(param_2);
    if ((int)param_3 < iVar1 + 0xc4) {
      FUN_10009934(PTR_s__ImcraStateInit_Error__bufsize___1000e780,param_3,iVar1 + 0xc4);
    }
    else {
      iVar1 = param_2[3];
      uVar6 = iVar1 * 2;
      if (uVar6 <= param_3 - 0xc4) {
        iVar4 = param_2[5];
        uVar8 = (param_3 - 0xc4) + iVar1 * -2;
        uVar3 = (iVar1 - iVar4) * 2;
        param_2[9] = param_2 + 0x31;
        iVar9 = (int)(param_2 + 0x31) + uVar6;
        if (uVar3 <= uVar8) {
          uVar8 = uVar8 + (iVar1 - iVar4) * -2;
          param_2[0xb] = iVar9;
          iVar9 = iVar9 + uVar3;
          if (uVar6 <= uVar8) {
            uVar8 = uVar8 + iVar1 * -2;
            param_2[0xc] = iVar9;
            iVar9 = iVar9 + uVar6;
            if ((uint)(iVar4 * 2) <= uVar8) {
              uVar8 = uVar8 + iVar4 * -2;
              uVar6 = param_2[4] * 2;
              param_2[0xd] = iVar9;
              iVar9 = iVar9 + iVar4 * 2;
              if (uVar6 <= uVar8) {
                iVar1 = param_2[7];
                uVar8 = uVar8 + param_2[4] * -2;
                param_2[0xe] = iVar9;
                iVar9 = iVar9 + uVar6;
                uVar6 = iVar1 * 4;
                if (uVar6 <= uVar8) {
                  uVar8 = uVar8 + iVar1 * -4;
                  param_2[0xf] = iVar9;
                  iVar9 = iVar9 + uVar6;
                  if (uVar6 <= uVar8) {
                    uVar8 = uVar8 + iVar1 * -4;
                    param_2[0x10] = iVar9;
                    iVar9 = iVar9 + uVar6;
                    if (uVar6 <= uVar8) {
                      uVar8 = uVar8 + iVar1 * -4;
                      param_2[0x11] = iVar9;
                      iVar9 = iVar9 + uVar6;
                      if (uVar6 <= uVar8) {
                        uVar8 = uVar8 + iVar1 * -4;
                        param_2[0x1e] = iVar9;
                        iVar9 = iVar9 + uVar6;
                        if (uVar6 <= uVar8) {
                          uVar8 = uVar8 + iVar1 * -4;
                          param_2[0x1f] = iVar9;
                          iVar9 = iVar9 + uVar6;
                          if (uVar6 <= uVar8) {
                            uVar8 = uVar8 + iVar1 * -4;
                            param_2[0x20] = iVar9;
                            iVar9 = iVar9 + uVar6;
                            if (uVar6 <= uVar8) {
                              uVar8 = uVar8 + iVar1 * -4;
                              uVar3 = iVar1 * 0x20;
                              param_2[0x21] = iVar9;
                              iVar9 = iVar9 + uVar6;
                              if (uVar3 <= uVar8) {
                                uVar8 = uVar8 + iVar1 * -0x20;
                                param_2[0x22] = iVar9;
                                iVar9 = iVar9 + uVar3;
                                if (uVar6 <= uVar8) {
                                  uVar8 = uVar8 + iVar1 * -4;
                                  param_2[0x23] = iVar9;
                                  iVar9 = iVar9 + uVar6;
                                  if (uVar3 <= uVar8) {
                                    uVar8 = uVar8 + iVar1 * -0x20;
                                    param_2[0x24] = iVar9;
                                    iVar9 = iVar9 + uVar3;
                                    if (uVar6 <= uVar8) {
                                      uVar8 = uVar8 + iVar1 * -4;
                                      param_2[0x25] = iVar9;
                                      puVar10 = (undefined4 *)(iVar9 + uVar6);
                                      if (uVar6 <= uVar8) {
                                        uVar8 = uVar8 + iVar1 * -4;
                                        param_2[0x26] = puVar10;
                                        puVar2 = puVar10 + iVar1;
                                        if (uVar6 <= uVar8) {
                                          uVar8 = uVar8 + iVar1 * -4;
                                          param_2[0x27] = puVar2;
                                          puVar7 = puVar2 + iVar1;
                                          if (uVar6 <= uVar8) {
                                            uVar8 = uVar8 + iVar1 * -4;
                                            param_2[0x28] = puVar7;
                                            if (uVar6 <= uVar8) {
                                              uVar8 = uVar8 + iVar1 * -4;
                                              param_2[0x29] = puVar7 + iVar1;
                                              puVar7 = puVar7 + iVar1 + iVar1;
                                              if (uVar6 <= uVar8) {
                                                uVar8 = uVar8 + iVar1 * -4;
                                                param_2[0x2a] = puVar7;
                                                puVar11 = puVar7 + iVar1;
                                                if (3 < uVar8) {
                                                  uVar8 = uVar8 - 4;
                                                  param_2[0x2b] = puVar11;
                                                  puVar12 = puVar11 + 1;
                                                  if (uVar6 <= uVar8) {
                                                    uVar8 = uVar8 + iVar1 * -4;
                                                    param_2[0x2c] = puVar12;
                                                    if (uVar6 <= uVar8) {
                                                      param_2[0x2d] = puVar12 + iVar1;
                                                      if (uVar6 <= uVar8 + iVar1 * -4) {
                                                        param_2[0x2e] = puVar12 + iVar1 + iVar1;
                                                        if (0 < iVar1) {
                                                          do {
                                                            *puVar7 = 0;
                                                            puVar7 = puVar7 + 1;
                                                          } while (puVar11 != puVar7);
                                                          do {
                                                            *puVar10 = 0;
                                                            puVar10 = puVar10 + 1;
                                                          } while (puVar2 != puVar10);
                                                        }
                                                        FUN_1000ee64();
                    /* WARNING: Bad instruction - Truncating control flow here */
                                                        halt_baddata();
                                                      }
                                                    }
                                                  }
                                                }
                                              }
                                            }
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      FUN_10009934(PTR_s__ImcraStateInit_Error__Not_enoug_1000e758);
    }
  }
  return 0;
}

