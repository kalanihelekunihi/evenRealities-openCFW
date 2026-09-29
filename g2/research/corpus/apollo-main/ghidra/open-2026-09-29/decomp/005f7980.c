
int TT_RunIns(int *param_1)

{
  byte bVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  int *piVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  uint uVar8;
  
  uVar8 = 0;
  if (((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
      (*(char *)((int)param_1 + 0x265) != '\0')) && (-1 < *(int *)(*param_1 + 8) << 0x12)) {
    *(byte *)((int)param_1 + 0x267) = *(byte *)(param_1 + 0x55) >> 2 & 1 ^ 1;
  }
  else {
    *(undefined1 *)((int)param_1 + 0x267) = 0;
  }
  *(undefined1 *)(param_1 + 0x9a) = 0;
  *(undefined1 *)((int)param_1 + 0x269) = 0;
  if ((param_1[0x60] + (uint)*(ushort *)(param_1 + 0x26)) * 2 < 0x1e) {
    uVar3 = 0x1e;
  }
  else {
    uVar3 = (param_1[0x60] + (uint)*(ushort *)(param_1 + 0x26)) * 2;
  }
  if (uVar3 < *(ushort *)(param_1 + 0x2f)) {
    if (0xffff < uVar3) {
      uVar3 = 0xffff;
    }
    *(short *)(param_1 + 0x2f) = (short)uVar3;
  }
  param_1[0x9b] = 0;
  param_1[0x9d] = 0;
  if ((short)param_1[0x26] == 0) {
    param_1[0x9c] = param_1[0x60] * 8 + 300;
  }
  else {
    if ((uint)*(ushort *)(param_1 + 0x26) * 10 < 0x32) {
      iVar4 = 0x32;
    }
    else {
      iVar4 = (uint)*(ushort *)(param_1 + 0x26) * 10;
    }
    if ((uint)param_1[0x60] / 10 < 0x32) {
      uVar3 = 0x32;
    }
    else {
      uVar3 = (uint)param_1[0x60] / 10;
    }
    param_1[0x9c] = uVar3 + iVar4;
  }
  if ((uint)(*(int *)(*param_1 + 0x10) * 100) < (uint)param_1[0x9c]) {
    param_1[0x9c] = *(int *)(*param_1 + 0x10) * 100;
  }
  param_1[0x9e] = param_1[0x9c];
  param_1[0x41] = 0;
  if ((short)param_1[0x37] == *(short *)((int)param_1 + 0xde)) {
    param_1[0x95] = DAT_005f8554;
    param_1[0x96] = DAT_005f8558;
    param_1[0x97] = DAT_005f855c;
    param_1[0x98] = DAT_005f8560;
  }
  else {
    param_1[0x95] = DAT_005f8544;
    param_1[0x96] = DAT_005f8548;
    param_1[0x97] = DAT_005f854c;
    param_1[0x98] = DAT_005f8550;
  }
  Compute_Funcs(param_1);
  Compute_Round(param_1,param_1[0x4f] & 0xff);
  while( true ) {
    *(undefined1 *)(param_1 + 0x5d) = *(undefined1 *)(param_1[0x5a] + param_1[0x5b]);
    param_1[0x5e] = (int)*(char *)(DAT_005f8564 + (uint)*(byte *)(param_1 + 0x5d));
    if (param_1[0x5e] < 0) break;
LAB_005f7b34:
    iVar4 = DAT_005f8768;
    if (param_1[0x5c] < param_1[0x5e] + param_1[0x5b]) goto LAB_005f7b6e;
    param_1[7] = param_1[4] - (uint)(*(byte *)(DAT_005f8768 + (uint)*(byte *)(param_1 + 0x5d)) >> 4)
    ;
    if (param_1[7] < 0) {
      if (*(char *)((int)param_1 + 0x235) != '\0') {
        param_1[3] = 0x81;
        goto LAB_005f7b72;
      }
      for (uVar2 = 0; uVar2 < *(byte *)(iVar4 + (uint)*(byte *)(param_1 + 0x5d)) >> 4;
          uVar2 = uVar2 + 1) {
        *(undefined4 *)(param_1[6] + (uint)uVar2 * 4) = 0;
      }
      param_1[7] = 0;
    }
    if ((char)param_1[0x5d] == -0x6f) {
      if (*(int *)(*param_1 + 700) != 0) {
        param_1[8] = **(int **)(*param_1 + 700) + param_1[7];
      }
    }
    else {
      param_1[8] = (*(byte *)(iVar4 + (uint)*(byte *)(param_1 + 0x5d)) & 0xf) + param_1[7];
    }
    if (param_1[5] < param_1[8]) {
      param_1[3] = 0x82;
      goto LAB_005f7b72;
    }
    *(undefined1 *)(param_1 + 0x5f) = 1;
    param_1[3] = 0;
    iVar4 = param_1[6] + param_1[7] * 4;
    bVar1 = *(byte *)(param_1 + 0x5d);
    if (((bVar1 == 0) || (bVar1 == 2)) || ((bVar1 < 2 || ((bVar1 == 4 || (bVar1 < 4)))))) {
LAB_005f7f1e:
      Ins_SxyTCA(param_1);
    }
    else if (bVar1 == 6) {
LAB_005f7f26:
      Ins_SPVTL(param_1);
    }
    else {
      if (bVar1 < 6) goto LAB_005f7f1e;
      if (bVar1 == 8) {
LAB_005f7f2e:
        Ins_SFVTL(param_1);
      }
      else {
        if (bVar1 < 8) goto LAB_005f7f26;
        if (bVar1 == 10) {
          Ins_SPVFS(param_1);
        }
        else {
          if (bVar1 < 10) goto LAB_005f7f2e;
          if (bVar1 == 0xc) {
            Ins_GPV(param_1);
          }
          else if (bVar1 < 0xc) {
            Ins_SFVFS(param_1);
          }
          else if (bVar1 == 0xe) {
            Ins_SFVTPV(param_1);
          }
          else if (bVar1 < 0xe) {
            Ins_GFV(param_1);
          }
          else if (bVar1 == 0x10) {
            Ins_SRP0(param_1);
          }
          else if (bVar1 < 0x10) {
            Ins_ISECT(param_1);
          }
          else if (bVar1 == 0x12) {
            Ins_SRP2(param_1);
          }
          else if (bVar1 < 0x12) {
            Ins_SRP1(param_1);
          }
          else if (bVar1 == 0x14) {
            Ins_SZP1(param_1);
          }
          else if (bVar1 < 0x14) {
            Ins_SZP0(param_1);
          }
          else if (bVar1 == 0x16) {
            Ins_SZPS(param_1);
          }
          else if (bVar1 < 0x16) {
            Ins_SZP2(param_1);
          }
          else if (bVar1 == 0x18) {
            Ins_RTG(param_1);
          }
          else if (bVar1 < 0x18) {
            Ins_SLOOP(param_1);
          }
          else if (bVar1 == 0x1a) {
            Ins_SMD(param_1);
          }
          else if (bVar1 < 0x1a) {
            Ins_RTHG(param_1);
          }
          else if (bVar1 == 0x1c) {
            Ins_JMPR(param_1);
          }
          else if (bVar1 < 0x1c) {
            Ins_ELSE(param_1);
          }
          else if (bVar1 == 0x1e) {
            Ins_SSWCI(param_1);
          }
          else if (bVar1 < 0x1e) {
            Ins_SCVTCI(param_1);
          }
          else if (bVar1 == 0x20) {
            Ins_DUP(iVar4);
          }
          else if (bVar1 < 0x20) {
            Ins_SSW(param_1);
          }
          else if (bVar1 == 0x22) {
            Ins_CLEAR(param_1);
          }
          else if (bVar1 < 0x22) {
            Ins_POP();
          }
          else if (bVar1 == 0x24) {
            Ins_DEPTH(param_1);
          }
          else if (bVar1 < 0x24) {
            Ins_SWAP(iVar4);
          }
          else if (bVar1 == 0x26) {
            Ins_MINDEX(param_1);
          }
          else if (bVar1 < 0x26) {
            Ins_CINDEX(param_1);
          }
          else if (bVar1 == 0x28) {
            Ins_UNKNOWN(param_1);
          }
          else if (bVar1 < 0x28) {
            Ins_ALIGNPTS(param_1);
          }
          else if (bVar1 == 0x2a) {
            Ins_LOOPCALL(param_1);
          }
          else if (bVar1 < 0x2a) {
            Ins_UTP(param_1);
          }
          else if (bVar1 == 0x2c) {
            Ins_FDEF(param_1);
          }
          else if (bVar1 < 0x2c) {
            Ins_CALL(param_1);
          }
          else if (bVar1 == 0x2e) {
LAB_005f8054:
            Ins_MDAP(param_1);
          }
          else if (bVar1 < 0x2e) {
            Ins_ENDF(param_1);
          }
          else if (bVar1 == 0x30) {
LAB_005f805c:
            Ins_IUP(param_1);
          }
          else {
            if (bVar1 < 0x30) goto LAB_005f8054;
            if (bVar1 == 0x32) {
LAB_005f8064:
              Ins_SHP(param_1);
            }
            else {
              if (bVar1 < 0x32) goto LAB_005f805c;
              if (bVar1 == 0x34) {
LAB_005f806c:
                Ins_SHC(param_1);
              }
              else {
                if (bVar1 < 0x34) goto LAB_005f8064;
                if (bVar1 == 0x36) {
LAB_005f8074:
                  Ins_SHZ(param_1);
                }
                else {
                  if (bVar1 < 0x36) goto LAB_005f806c;
                  if (bVar1 == 0x38) {
                    Ins_SHPIX(param_1);
                  }
                  else {
                    if (bVar1 < 0x38) goto LAB_005f8074;
                    if (bVar1 == 0x3a) {
LAB_005f808c:
                      Ins_MSIRP(param_1);
                    }
                    else if (bVar1 < 0x3a) {
                      Ins_IP(param_1);
                    }
                    else if (bVar1 == 0x3c) {
                      Ins_ALIGNRP(param_1);
                    }
                    else {
                      if (bVar1 < 0x3c) goto LAB_005f808c;
                      if (bVar1 == 0x3e) {
LAB_005f80a4:
                        Ins_MIAP(param_1);
                      }
                      else if (bVar1 < 0x3e) {
                        Ins_RTDG(param_1);
                      }
                      else if (bVar1 == 0x40) {
                        Ins_NPUSHB(param_1);
                      }
                      else {
                        if (bVar1 < 0x40) goto LAB_005f80a4;
                        if (bVar1 == 0x42) {
                          Ins_WS(param_1);
                        }
                        else if (bVar1 < 0x42) {
                          Ins_NPUSHW(param_1);
                        }
                        else if (bVar1 == 0x44) {
                          Ins_WCVTP(param_1);
                        }
                        else if (bVar1 < 0x44) {
                          Ins_RS(param_1);
                        }
                        else if (bVar1 == 0x46) {
LAB_005f80dc:
                          Ins_GC(param_1);
                        }
                        else if (bVar1 < 0x46) {
                          Ins_RCVT(param_1);
                        }
                        else if (bVar1 == 0x48) {
                          Ins_SCFS(param_1);
                        }
                        else {
                          if (bVar1 < 0x48) goto LAB_005f80dc;
                          if ((bVar1 == 0x4a) || (bVar1 < 0x4a)) {
                            Ins_MD(param_1);
                          }
                          else if (bVar1 == 0x4c) {
                            Ins_MPS(param_1);
                          }
                          else if (bVar1 < 0x4c) {
                            Ins_MPPEM(param_1);
                          }
                          else if (bVar1 == 0x4e) {
                            Ins_FLIPOFF(param_1);
                          }
                          else if (bVar1 < 0x4e) {
                            Ins_FLIPON(param_1);
                          }
                          else if (bVar1 == 0x50) {
                            Ins_LT(iVar4);
                          }
                          else if (bVar1 < 0x50) {
                            Ins_DEBUG(param_1);
                          }
                          else if (bVar1 == 0x52) {
                            Ins_GT(iVar4);
                          }
                          else if (bVar1 < 0x52) {
                            Ins_LTEQ(iVar4);
                          }
                          else if (bVar1 == 0x54) {
                            Ins_EQ(iVar4);
                          }
                          else if (bVar1 < 0x54) {
                            Ins_GTEQ(iVar4);
                          }
                          else if (bVar1 == 0x56) {
                            Ins_ODD(param_1);
                          }
                          else if (bVar1 < 0x56) {
                            Ins_NEQ(iVar4);
                          }
                          else if (bVar1 == 0x58) {
                            Ins_IF(param_1);
                          }
                          else if (bVar1 < 0x58) {
                            Ins_EVEN(param_1);
                          }
                          else if (bVar1 == 0x5a) {
                            Ins_AND(iVar4);
                          }
                          else if (bVar1 < 0x5a) {
                            Ins_EIF();
                          }
                          else if (bVar1 == 0x5c) {
                            Ins_NOT(iVar4);
                          }
                          else if (bVar1 < 0x5c) {
                            Ins_OR(iVar4);
                          }
                          else if (bVar1 == 0x5e) {
                            Ins_SDB(param_1);
                          }
                          else if (bVar1 < 0x5e) {
                            Ins_DELTAP(param_1);
                          }
                          else if (bVar1 == 0x60) {
                            Ins_ADD(iVar4);
                          }
                          else if (bVar1 < 0x60) {
                            Ins_SDS(param_1);
                          }
                          else if (bVar1 == 0x62) {
                            Ins_DIV(param_1);
                          }
                          else if (bVar1 < 0x62) {
                            Ins_SUB(iVar4);
                          }
                          else if (bVar1 == 100) {
                            Ins_ABS(iVar4);
                          }
                          else if (bVar1 < 100) {
                            Ins_MUL(iVar4);
                          }
                          else if (bVar1 == 0x66) {
                            Ins_FLOOR(iVar4);
                          }
                          else if (bVar1 < 0x66) {
                            Ins_NEG(iVar4);
                          }
                          else if (bVar1 == 0x68) {
LAB_005f81da:
                            Ins_ROUND(param_1);
                          }
                          else if (bVar1 < 0x68) {
                            Ins_CEILING(iVar4);
                          }
                          else {
                            if ((bVar1 == 0x6a) || (bVar1 < 0x6a)) goto LAB_005f81da;
                            if (bVar1 != 0x6c) {
                              if (bVar1 < 0x6c) goto LAB_005f81da;
                              if ((bVar1 != 0x6e) && (0x6d < bVar1)) {
                                if (bVar1 == 0x70) {
                                  Ins_WCVTF(param_1);
                                }
                                else {
                                  if (bVar1 < 0x70) goto LAB_005f81e2;
                                  if ((bVar1 == 0x72) || (bVar1 < 0x72)) {
                                    Ins_DELTAP(param_1);
                                  }
                                  else if ((bVar1 == 0x74) || (bVar1 < 0x74)) {
LAB_005f81fa:
                                    Ins_DELTAC(param_1);
                                  }
                                  else if (bVar1 == 0x76) {
                                    Ins_SROUND(param_1);
                                  }
                                  else {
                                    if (bVar1 < 0x76) goto LAB_005f81fa;
                                    if (bVar1 == 0x78) {
                                      Ins_JROT(param_1);
                                    }
                                    else if (bVar1 < 0x78) {
                                      Ins_S45ROUND(param_1);
                                    }
                                    else if (bVar1 == 0x7a) {
                                      Ins_ROFF(param_1);
                                    }
                                    else if (bVar1 < 0x7a) {
                                      Ins_JROF(param_1);
                                    }
                                    else if (bVar1 == 0x7c) {
                                      Ins_RUTG(param_1);
                                    }
                                    else if (bVar1 < 0x7c) {
                                      Ins_UNKNOWN(param_1);
                                    }
                                    else if (bVar1 == 0x7e) {
                                      Ins_SANGW();
                                    }
                                    else if (bVar1 < 0x7e) {
                                      Ins_RDTG(param_1);
                                    }
                                    else if (bVar1 == 0x80) {
                                      Ins_FLIPPT(param_1);
                                    }
                                    else if (bVar1 < 0x80) {
                                      Ins_AA();
                                    }
                                    else if (bVar1 == 0x82) {
                                      Ins_FLIPRGOFF(param_1);
                                    }
                                    else if (bVar1 < 0x82) {
                                      Ins_FLIPRGON(param_1);
                                    }
                                    else if ((bVar1 == 0x84) || (bVar1 < 0x84)) {
                                      Ins_UNKNOWN(param_1);
                                    }
                                    else if (bVar1 == 0x86) {
LAB_005f8276:
                                      Ins_SDPVTL(param_1);
                                    }
                                    else if (bVar1 < 0x86) {
                                      Ins_SCANCTRL(param_1);
                                    }
                                    else if (bVar1 == 0x88) {
                                      Ins_GETINFO(param_1);
                                    }
                                    else {
                                      if (bVar1 < 0x88) goto LAB_005f8276;
                                      if (bVar1 == 0x8a) {
                                        Ins_ROLL(iVar4);
                                      }
                                      else if (bVar1 < 0x8a) {
                                        Ins_IDEF(param_1);
                                      }
                                      else if (bVar1 == 0x8c) {
                                        Ins_MIN(iVar4);
                                      }
                                      else if (bVar1 < 0x8c) {
                                        Ins_MAX(iVar4);
                                      }
                                      else if (bVar1 == 0x8e) {
                                        Ins_INSTCTRL(param_1);
                                      }
                                      else if (bVar1 < 0x8e) {
                                        Ins_SCANTYPE(param_1);
                                      }
                                      else if ((bVar1 == 0x90) || (bVar1 < 0x90)) {
                                        Ins_UNKNOWN(param_1);
                                      }
                                      else if (bVar1 == 0x92) {
                                        if (*(int *)(*param_1 + 700) == 0) {
                                          Ins_UNKNOWN(param_1);
                                        }
                                        else {
                                          Ins_GETDATA(iVar4);
                                        }
                                      }
                                      else if (bVar1 < 0x92) {
                                        if (*(int *)(*param_1 + 700) == 0) {
                                          Ins_UNKNOWN(param_1);
                                        }
                                        else {
                                          Ins_GETVARIATION(param_1);
                                        }
                                      }
                                      else if (bVar1 < 0xe0) {
                                        if (bVar1 < 0xc0) {
                                          if (bVar1 < 0xb8) {
                                            if (bVar1 < 0xb0) {
                                              Ins_UNKNOWN(param_1);
                                            }
                                            else {
                                              Ins_PUSHB(param_1);
                                            }
                                          }
                                          else {
                                            Ins_PUSHW(param_1);
                                          }
                                        }
                                        else {
                                          Ins_MDRP(param_1);
                                        }
                                      }
                                      else {
                                        Ins_MIRP(param_1);
                                      }
                                    }
                                  }
                                }
                                goto LAB_005f7ef8;
                              }
                            }
LAB_005f81e2:
                            Ins_NROUND(param_1);
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
LAB_005f7ef8:
    if (param_1[3] == 0) {
      param_1[4] = param_1[8];
      if ((char)param_1[0x5f] != '\0') {
        param_1[0x5b] = param_1[0x5e] + param_1[0x5b];
      }
      uVar8 = uVar8 + 1;
      if (DAT_005f8f04 <= uVar8) {
        return 0x8b;
      }
    }
    else {
      if (param_1[3] != 0x80) goto LAB_005f7b72;
      puVar6 = (undefined4 *)param_1[0x69];
      puVar7 = puVar6 + param_1[0x67] * 6;
      while( true ) {
        if (puVar7 <= puVar6) {
          param_1[3] = 0x80;
          goto LAB_005f7b72;
        }
        if ((*(char *)(puVar6 + 4) != '\0') &&
           ((uint)*(byte *)(param_1 + 0x5d) == (puVar6[3] & 0xff))) break;
        puVar6 = puVar6 + 6;
      }
      if (param_1[0x6d] <= param_1[0x6c]) {
        param_1[3] = 0x86;
        goto LAB_005f7b72;
      }
      piVar5 = (int *)(param_1[0x6e] + param_1[0x6c] * 0x10);
      *piVar5 = param_1[0x59];
      piVar5[1] = param_1[0x5b] + 1;
      piVar5[2] = 1;
      piVar5[3] = (int)puVar6;
      iVar4 = Ins_Goto_CodeRange(param_1,*puVar6,puVar6[1]);
      if (iVar4 == 1) goto LAB_005f7b72;
    }
    if (param_1[0x5c] <= param_1[0x5b]) {
      if (param_1[0x6c] < 1) {
        return 0;
      }
      param_1[3] = 0x83;
      goto LAB_005f7b72;
    }
    if ((char)param_1[0x7b] != '\0') {
      return 0;
    }
  }
  if (param_1[0x5b] + 1 < param_1[0x5c]) {
    param_1[0x5e] = 2 - (uint)*(byte *)(param_1[0x5a] + param_1[0x5b] + 1) * param_1[0x5e];
    goto LAB_005f7b34;
  }
LAB_005f7b6e:
  param_1[3] = 0x83;
LAB_005f7b72:
  return param_1[3];
}

