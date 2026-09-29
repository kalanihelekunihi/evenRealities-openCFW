
undefined8 FUN_0044c178(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uStack_28;
  undefined4 uStack_24;
  
  bVar4 = 0;
  uVar5 = 0;
  uStack_28 = param_3;
  uStack_24 = param_4;
  do {
    if ((*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4 <= uVar5) {
      uVar5 = (uint)bVar4;
LAB_0044c444:
      return CONCAT44(uStack_28,uVar5);
    }
    if ((-1 < *(int *)(*(int *)(param_1 + 0xc) + uVar5 * 8 + 4) << 6) &&
       (uVar2 = FUN_0044b85c(*(uint *)(*(int *)(param_1 + 0xc) + uVar5 * 8 + 4) & 0xffffff),
       ((uVar2 & 0xffff & ~param_2) == 0) != ((uVar2 & 0xffff & ~param_3) == 0))) {
      uVar6 = *(undefined4 *)(*(int *)(param_1 + 0xc) + uVar5 * 8);
      bVar1 = false;
      iVar3 = FUN_00482946(uVar6,0x10,&uStack_28);
      if (iVar3 == 0) {
        iVar3 = FUN_00482946(uVar6,0x11,&uStack_28);
        if (iVar3 == 0) {
          iVar3 = FUN_00482946(uVar6,0x12,&uStack_28);
          if (iVar3 == 0) {
            iVar3 = FUN_00482946(uVar6,0x13,&uStack_28);
            if (iVar3 == 0) {
              iVar3 = FUN_00482946(uVar6,0x15,&uStack_28);
              if (iVar3 == 0) {
                iVar3 = FUN_00482946(uVar6,0x14,&uStack_28);
                if (iVar3 == 0) {
                  iVar3 = FUN_00482946(uVar6,0x16,&uStack_28);
                  if (iVar3 == 0) {
                    iVar3 = FUN_00482946(uVar6,0x6c,&uStack_28);
                    if (iVar3 == 0) {
                      iVar3 = FUN_00482946(uVar6,0x6d,&uStack_28);
                      if (iVar3 == 0) {
                        iVar3 = FUN_00482946(uVar6,1,&uStack_28);
                        if (iVar3 == 0) {
                          iVar3 = FUN_00482946(uVar6,2,&uStack_28);
                          if (iVar3 == 0) {
                            iVar3 = FUN_00482946(uVar6,4,&uStack_28);
                            if (iVar3 == 0) {
                              iVar3 = FUN_00482946(uVar6,5,&uStack_28);
                              if (iVar3 == 0) {
                                iVar3 = FUN_00482946(uVar6,6,&uStack_28);
                                if (iVar3 == 0) {
                                  iVar3 = FUN_00482946(uVar6,7,&uStack_28);
                                  if (iVar3 == 0) {
                                    iVar3 = FUN_00482946(uVar6,0x30,&uStack_28);
                                    if (iVar3 != 0) {
                                      bVar1 = true;
                                    }
                                  }
                                  else {
                                    bVar1 = true;
                                  }
                                }
                                else {
                                  bVar1 = true;
                                }
                              }
                              else {
                                bVar1 = true;
                              }
                            }
                            else {
                              bVar1 = true;
                            }
                          }
                          else {
                            bVar1 = true;
                          }
                        }
                        else {
                          bVar1 = true;
                        }
                      }
                      else {
                        bVar1 = true;
                      }
                    }
                    else {
                      bVar1 = true;
                    }
                  }
                  else {
                    bVar1 = true;
                  }
                }
                else {
                  bVar1 = true;
                }
              }
              else {
                bVar1 = true;
              }
            }
            else {
              bVar1 = true;
            }
          }
          else {
            bVar1 = true;
          }
        }
        else {
          bVar1 = true;
        }
      }
      else {
        bVar1 = true;
      }
      if (bVar1) {
        uVar5 = 3;
        goto LAB_0044c444;
      }
      iVar3 = FUN_00482946(uVar6,0x6a,&uStack_28);
      if (iVar3 == 0) {
        iVar3 = FUN_00482946(uVar6,0x6b,&uStack_28);
        if (iVar3 == 0) {
          iVar3 = FUN_00482946(uVar6,0x70,&uStack_28);
          if (iVar3 == 0) {
            iVar3 = FUN_00482946(uVar6,0x6e,&uStack_28);
            if (iVar3 == 0) {
              iVar3 = FUN_00482946(uVar6,0x6f,&uStack_28);
              if (iVar3 == 0) {
                iVar3 = FUN_00482946(uVar6,0x3a,&uStack_28);
                if (iVar3 == 0) {
                  iVar3 = FUN_00482946(uVar6,0x3b,&uStack_28);
                  if (iVar3 == 0) {
                    iVar3 = FUN_00482946(uVar6,0x38,&uStack_28);
                    if (iVar3 == 0) {
                      iVar3 = FUN_00482946(uVar6,0x3c,&uStack_28);
                      if (iVar3 == 0) {
                        iVar3 = FUN_00482946(uVar6,0x3e,&uStack_28);
                        if (iVar3 == 0) {
                          iVar3 = FUN_00482946(uVar6,0x40,&uStack_28);
                          if (iVar3 == 0) {
                            iVar3 = FUN_00482946(uVar6,0x41,&uStack_28);
                            if (iVar3 == 0) {
                              iVar3 = FUN_00482946(uVar6,0x42,&uStack_28);
                              if (iVar3 == 0) {
                                iVar3 = FUN_00482946(uVar6,0x48,&uStack_28);
                                if (iVar3 == 0) {
                                  if (bVar4 == 0) {
                                    bVar4 = 1;
                                  }
                                }
                                else {
                                  bVar4 = 2;
                                }
                              }
                              else {
                                bVar4 = 2;
                              }
                            }
                            else {
                              bVar4 = 2;
                            }
                          }
                          else {
                            bVar4 = 2;
                          }
                        }
                        else {
                          bVar4 = 2;
                        }
                      }
                      else {
                        bVar4 = 2;
                      }
                    }
                    else {
                      bVar4 = 2;
                    }
                  }
                  else {
                    bVar4 = 2;
                  }
                }
                else {
                  bVar4 = 2;
                }
              }
              else {
                bVar4 = 2;
              }
            }
            else {
              bVar4 = 2;
            }
          }
          else {
            bVar4 = 2;
          }
        }
        else {
          bVar4 = 2;
        }
      }
      else {
        bVar4 = 2;
      }
    }
    uVar5 = uVar5 + 1;
  } while( true );
}

