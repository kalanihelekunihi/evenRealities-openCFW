
undefined8 AttcDiscCharCmpl(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if ((*(char *)(param_2 + 2) == '\x04') || (*(char *)(param_2 + 2) == '\x02')) {
    if (*(char *)(param_2 + 2) == '\x04') {
      bVar1 = attcDiscProcChar(param_1,param_2);
      iVar4 = param_2;
    }
    else {
      bVar1 = attcDiscProcDesc(param_1,param_2);
      iVar4 = param_2;
    }
    if ((bVar1 != 0) && (bVar1 != 0x79)) {
      FUN_0043c0e4(*(undefined4 *)(param_1 + 4),(uint)*(byte *)(param_1 + 0xc) << 1,0);
    }
    uVar3 = (uint)bVar1;
  }
  else {
    iVar4 = param_2;
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,&DAT_0056c350,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c34c,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056c34c,DAT_0056c360,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0056c354,&DAT_0056c364,3), iVar2 != 0)) {
              WsfTrace(DAT_0056c34c,DAT_0056c36c,*(undefined1 *)(param_2 + 2));
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x2a6;
              FUN_0043d574(4,&DAT_0056c354,DAT_0056c384,DAT_0056c380,0x2a6,DAT_0056c36c,
                           *(undefined1 *)(param_2 + 2));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            iVar4 = 0x2a6;
            FUN_0043d574(3,&DAT_0056c354,DAT_0056c384,DAT_0056c380,0x2a6,DAT_0056c36c,
                         *(undefined1 *)(param_2 + 2));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0x2a6;
          FUN_0043d574(2,&DAT_0056c354,DAT_0056c384,DAT_0056c380,0x2a6,DAT_0056c36c,
                       *(undefined1 *)(param_2 + 2));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar4 = 0x2a6;
        FUN_0043d574(1,&DAT_0056c354,DAT_0056c384,DAT_0056c380,0x2a6,DAT_0056c36c,
                     *(undefined1 *)(param_2 + 2));
      }
    }
    uVar3 = 0x75;
  }
  return CONCAT44(iVar4,uVar3);
}

