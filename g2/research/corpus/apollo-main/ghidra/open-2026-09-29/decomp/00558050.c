
undefined8 FUN_00558050(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  byte bVar3;
  
  if (param_1 == (byte *)0x0) {
    uVar1 = 0;
  }
  else {
    bVar3 = *param_1;
    if (bVar3 == 1) {
      if (param_1[4] < 2) {
        iVar2 = FUN_00558040(param_1[5]);
        if (iVar2 == 0) {
          uVar1 = 0;
        }
        else {
          iVar2 = FUN_00558040(param_1[6]);
          if (iVar2 == 0) {
            uVar1 = 0;
          }
          else {
            uVar1 = 1;
          }
        }
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      if (bVar3 != 0) {
        if (bVar3 == 3) {
          if (param_1[4] < 3) {
            if (param_1[5] < 2) {
              if (param_1[6] < 2) {
                uVar1 = 1;
              }
              else {
                uVar1 = 0;
              }
            }
            else {
              uVar1 = 0;
            }
          }
          else {
            uVar1 = 0;
          }
          goto LAB_00558140;
        }
        if (bVar3 < 3) {
          if (param_1[4] < 3) {
            if (param_1[5] < 2) {
              if (param_1[6] < 2) {
                if (param_1[7] < 4) {
                  for (bVar3 = 0; bVar3 < param_1[7]; bVar3 = bVar3 + 1) {
                    iVar2 = FUN_00558040((param_1 + 4)[bVar3 + 4]);
                    if (iVar2 == 0) {
                      uVar1 = 0;
                      goto LAB_00558140;
                    }
                  }
                  uVar1 = 1;
                }
                else {
                  uVar1 = 0;
                }
              }
              else {
                uVar1 = 0;
              }
            }
            else {
              uVar1 = 0;
            }
          }
          else {
            uVar1 = 0;
          }
          goto LAB_00558140;
        }
        if (bVar3 == 4) {
          if (param_1[4] < 3) {
            if (param_1[5] < 4) {
              if (param_1[6] < 4) {
                if (param_1[0x14] < 4) {
                  uVar1 = 1;
                }
                else {
                  uVar1 = 0;
                }
              }
              else {
                uVar1 = 0;
              }
            }
            else {
              uVar1 = 0;
            }
          }
          else {
            uVar1 = 0;
          }
          goto LAB_00558140;
        }
      }
      uVar1 = 0;
    }
  }
LAB_00558140:
  return CONCAT44(param_4,uVar1);
}

