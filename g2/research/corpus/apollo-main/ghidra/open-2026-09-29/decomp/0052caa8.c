
char attsCsfActClientState(ushort param_1,uint param_2,int param_3)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  char cVar4;
  
  iVar2 = DAT_0052d07c;
  cVar4 = '\0';
  if (((param_2 & 0xff) == 2) || ((param_2 & 0xff) == 0x1e)) {
    cVar4 = '\0';
  }
  else {
    pbVar3 = (byte *)(DAT_0052d07c + (uint)param_1 * 2);
    if (pbVar3[1] == 3) {
      if (-1 < (int)(param_2 << 0x19)) {
        pbVar3[1] = 1;
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,&DAT_0052cd28,3), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,DAT_0052d08c,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,DAT_0052d4fc,4), iVar1 != 0)) {
              iVar1 = FUN_004c9c50();
              if (iVar1 == 0) {
                iVar1 = FUN_004c9c50();
                if ((iVar1 == 0) ||
                   (iVar1 = FUN_0044b610(&DAT_0052cd2c,&DAT_0052cf24,3), iVar1 != 0)) {
                  WsfTrace(DAT_0052d4fc,DAT_0052d500,param_1 + 1,1);
                }
              }
              else {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,0xb3,DAT_0052d500,
                               param_1 + 1,1);
                }
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,0xb3,DAT_0052d500,param_1 + 1
                             ,1);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,0xb3,DAT_0052d500,param_1 + 1,1
                          );
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,0xb3,DAT_0052d500,param_1 + 1,1);
          }
        }
      }
      if (((int)(param_2 << 0x19) < 0) || ((int)((uint)*pbVar3 << 0x1f) < 0)) {
        cVar4 = '\x12';
      }
    }
    else if (pbVar3[1] == 1) {
      if ((int)(param_2 << 0x19) < 0) {
        cVar4 = '\x12';
      }
      else {
        pbVar3[1] = 0;
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,&DAT_0052cd28,3), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,DAT_0052d08c,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d4fc,DAT_0052d4fc,4), iVar1 != 0)) {
              iVar1 = FUN_004c9c50();
              if (iVar1 == 0) {
                iVar1 = FUN_004c9c50();
                if ((iVar1 == 0) ||
                   (iVar1 = FUN_0044b610(&DAT_0052d070,&DAT_0052cf24,3), iVar1 != 0)) {
                  WsfTrace(DAT_0052d4fc,DAT_0052d500,param_1 + 1,0);
                }
              }
              else {
                iVar1 = FUN_0043d0ce();
                if (iVar1 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_0052d070,DAT_0052d088,DAT_0052d504,200,DAT_0052d500,
                               param_1 + 1,0);
                }
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,200,DAT_0052d500,param_1 + 1,
                             0);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,200,DAT_0052d500,param_1 + 1,0)
              ;
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_0052cd2c,DAT_0052d088,DAT_0052d504,200,DAT_0052d500,param_1 + 1,0);
          }
        }
        if (*(int *)(iVar2 + 8) != 0) {
          (**(code **)(iVar2 + 8))((char)param_1 + '\x01',pbVar3[1],pbVar3);
        }
      }
    }
    if ((((param_2 & 0xff) == 8) &&
        ((ushort)((ushort)*(byte *)(param_3 + 0xe) * 0x100 + (ushort)*(byte *)(param_3 + 0xd)) ==
         0x2b2a)) && (cVar4 = '\0', *(char *)(iVar2 + 0xc) != '\0')) {
      pbVar3[1] = 2;
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,&DAT_0052d074,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,DAT_0052d08c,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,DAT_0052d4fc,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052d070,&DAT_0052cf24,3), iVar2 != 0))
              {
                WsfTrace(DAT_0052d4fc,DAT_0052d500,param_1 + 1,2);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xef,DAT_0052d500,param_1 + 1
                             ,2);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xef,DAT_0052d500,param_1 + 1,2
                          );
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xef,DAT_0052d500,param_1 + 1,2);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xef,DAT_0052d500,param_1 + 1,2);
        }
      }
    }
    if (cVar4 == '\x12') {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,&DAT_0052d074,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,DAT_0052d08c,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d4fc,DAT_0052d4fc,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052d070,&DAT_0052d078,3), iVar2 != 0))
              {
                WsfTrace(DAT_0052d4fc,DAT_0052da18,param_1 + 1,param_2 & 0xff);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xf6,DAT_0052da18,param_1 + 1
                             ,param_2 & 0xff);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xf6,DAT_0052da18,param_1 + 1,
                           param_2 & 0xff);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xf6,DAT_0052da18,param_1 + 1,
                         param_2 & 0xff);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_0052d070,DAT_0052d088,DAT_0052d504,0xf6,DAT_0052da18,param_1 + 1,
                       param_2 & 0xff);
        }
      }
    }
  }
  return cVar4;
}

