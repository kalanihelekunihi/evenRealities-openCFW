
undefined4 FUN_005a4334(uint param_1,uint param_2,char *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  char acStack_30 [28];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_00439c04(acStack_30,DAT_005a4e5c,0x1c);
  *param_3 = acStack_30[(param_1 >> 2) + (param_2 >> 2) * 5];
  if (*param_3 == '\x1a') {
    uVar1 = 7;
  }
  else {
    if ((param_2 == 0) && (param_1 == 8)) {
      *param_3 = '\x15';
    }
    else if ((param_2 == 8) && (param_1 == 0)) {
      *param_3 = '\x16';
    }
    if (((param_2 == 8) && (param_1 == 0xc)) || ((param_2 == 0xc && (param_1 == 8)))) {
      *param_3 = '\x17';
    }
    if (*param_3 == '\x19') {
      if (((((param_2 & 3) == 0) || (4 < param_2 >> 2)) || ((param_1 & 3) != 0)) ||
         (4 < param_1 >> 2)) {
        if ((((param_2 & 3) == 0) && (param_2 >> 2 < 5)) &&
           (((param_1 & 3) != 0 && (param_1 >> 2 < 5)))) {
          if ((param_2 == 8) && (param_1 == 9)) {
            *param_3 = '\r';
          }
          else if ((param_2 == 0) && (param_1 == 1)) {
            *param_3 = '\x0e';
          }
          else {
            *param_3 = '\x18';
          }
        }
        else if (((((param_2 & 3) < 2) || (4 < param_2 >> 2)) || (1 < (param_1 & 3))) ||
                (4 < param_1 >> 2)) {
          if (((((param_2 & 3) < 2) && (param_2 >> 2 < 5)) && (1 < (param_1 & 3))) &&
             (param_1 >> 2 < 5)) {
            if ((param_2 == 9) && (param_1 == 10)) {
              *param_3 = '\x11';
            }
            else if ((param_2 == 1) && (param_1 == 2)) {
              *param_3 = '\x12';
            }
            else {
              *param_3 = '\x13';
            }
          }
          else if (((param_2 == 10) && (param_1 == 0xb)) || ((param_2 == 0xb && (param_1 == 10)))) {
            *param_3 = '\x14';
          }
          else {
            *param_3 = '\x18';
          }
        }
        else if (((param_2 == 2) && (param_1 == 1)) || ((param_2 == 10 && (param_1 == 9)))) {
          *param_3 = '\x0f';
        }
        else {
          *param_3 = '\x10';
        }
      }
      else if ((param_2 == 9) && (param_1 == 8)) {
        *param_3 = '\v';
      }
      else if ((param_2 == 1) && (param_1 == 0)) {
        *param_3 = '\f';
      }
      else {
        *param_3 = '\x18';
      }
    }
    uVar1 = 0;
  }
  return uVar1;
}

