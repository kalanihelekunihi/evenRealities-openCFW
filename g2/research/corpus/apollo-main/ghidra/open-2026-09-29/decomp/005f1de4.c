
int ft_var_get_value_pointer(int param_1,int param_2)

{
  int iVar1;
  
  if (param_2 - DAT_005f252c == 0) {
    param_1 = param_1 + 0x1ce;
  }
  else {
    iVar1 = (param_2 - DAT_005f252c) - DAT_005f2530;
    if (iVar1 == 0) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 1) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234);
      }
    }
    else if (iVar1 == 1) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 2) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 4;
      }
    }
    else if (iVar1 == 2) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 3) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 8;
      }
    }
    else if (iVar1 == 3) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 4) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0xc;
      }
    }
    else if (iVar1 == 4) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 5) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x10;
      }
    }
    else if (iVar1 == 5) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 6) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x14;
      }
    }
    else if (iVar1 == 6) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 7) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x18;
      }
    }
    else if (iVar1 == 7) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 8) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x1c;
      }
    }
    else if (iVar1 == 8) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 9) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x20;
      }
    }
    else if (iVar1 + -9 == 0) {
      if ((int)(*(ushort *)(param_1 + 0x232) - 1) < 10) {
        param_1 = 0;
      }
      else {
        param_1 = *(int *)(param_1 + 0x234) + 0x24;
      }
    }
    else {
      iVar1 = (iVar1 + -9) - DAT_005f2534;
      if (iVar1 == 0) {
        param_1 = param_1 + 0x1ba;
      }
      else {
        iVar1 = iVar1 - DAT_005f2538;
        if (iVar1 == 0) {
          param_1 = param_1 + 0x1c0;
        }
        else if (iVar1 == 3) {
          param_1 = param_1 + 0x1c2;
        }
        else if (iVar1 == 0x305) {
          param_1 = param_1 + 0xee;
        }
        else if (iVar1 == 0x60d) {
          param_1 = param_1 + 0xec;
        }
        else if (iVar1 + -0x612 == 0) {
          param_1 = param_1 + 0xea;
        }
        else {
          iVar1 = (iVar1 + -0x612) - DAT_005f253c;
          if (iVar1 == 0) {
            param_1 = param_1 + 0x1bc;
          }
          else {
            iVar1 = iVar1 - DAT_005f2540;
            if (iVar1 == 0) {
              param_1 = param_1 + 0x1be;
            }
            else {
              iVar1 = iVar1 - DAT_005f2544;
              if (iVar1 == 0) {
                param_1 = param_1 + 0x182;
              }
              else if (iVar1 == 4) {
                param_1 = param_1 + 0x17e;
              }
              else if (iVar1 == 0x100) {
                param_1 = param_1 + 0x184;
              }
              else if (iVar1 + -0x104 == 0) {
                param_1 = param_1 + 0x180;
              }
              else {
                iVar1 = (iVar1 + -0x104) - DAT_005f2548;
                if (iVar1 == 0) {
                  param_1 = param_1 + 0x18a;
                }
                else if (iVar1 == 4) {
                  param_1 = param_1 + 0x186;
                }
                else if (iVar1 == 0x100) {
                  param_1 = param_1 + 0x18c;
                }
                else if (iVar1 + -0x104 == 0) {
                  param_1 = param_1 + 0x188;
                }
                else {
                  iVar1 = (iVar1 + -0x104) - DAT_005f254c;
                  if (iVar1 == 0) {
                    param_1 = param_1 + 400;
                  }
                  else {
                    iVar1 = iVar1 + -4;
                    if (iVar1 == 0) {
                      param_1 = param_1 + 0x18e;
                    }
                    else {
                      iVar1 = iVar1 - DAT_005f2550;
                      if (iVar1 == 0) {
                        param_1 = param_1 + 0x1e4;
                      }
                      else {
                        iVar1 = iVar1 + -4;
                        if (iVar1 == 0) {
                          param_1 = param_1 + 0x1e6;
                        }
                        else {
                          iVar1 = iVar1 - DAT_005f2554;
                          if (iVar1 == 0) {
                            param_1 = param_1 + 300;
                          }
                          else {
                            iVar1 = iVar1 - DAT_005f2558;
                            if (iVar1 == 0) {
                              param_1 = param_1 + 0x13e;
                            }
                            else if (iVar1 == 0x308) {
                              param_1 = param_1 + 0x13c;
                            }
                            else if (iVar1 + -0x30d == 0) {
                              param_1 = param_1 + 0x13a;
                            }
                            else {
                              iVar1 = (iVar1 + -0x30d) - DAT_005f253c;
                              if (iVar1 == 0) {
                                param_1 = param_1 + 0x12e;
                              }
                              else if (iVar1 == DAT_005f2540) {
                                param_1 = param_1 + 0x130;
                              }
                              else if (iVar1 - DAT_005f2540 == DAT_005f255c) {
                                param_1 = param_1 + 0x1cc;
                              }
                              else {
                                param_1 = 0;
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
  return param_1;
}

