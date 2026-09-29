
undefined8 FUN_00531f20(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = param_1;
  if ((param_1 & 0xff) == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,&DAT_00532170,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532624,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532634,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00532238,&DAT_005322b8,3), iVar1 != 0)) {
              WsfTrace(DAT_00532624,DAT_00532914,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar3 = 0xc3;
              param_2 = DAT_00532914;
              FUN_0043d574(4,&DAT_00532238,DAT_00532630,DAT_00532918,0xc3,DAT_00532914,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar3 = 0xc3;
            param_2 = DAT_00532914;
            FUN_0043d574(3,&DAT_00532238,DAT_00532630,DAT_00532918,0xc3,DAT_00532914,param_1 & 0xff)
            ;
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 0xc3;
          param_2 = DAT_00532914;
          FUN_0043d574(2,&DAT_00532238,DAT_00532630,DAT_00532918,0xc3,DAT_00532914,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xc3;
        param_2 = DAT_00532914;
        FUN_0043d574(1,&DAT_00532238,DAT_00532630,DAT_00532918,0xc3,DAT_00532914,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else {
    iVar1 = DAT_00532638 + (param_1 & 0xff) * 0x10;
    *(undefined1 *)(iVar1 + -8) = 0;
    *(undefined1 *)(iVar1 + -7) = 0;
    *(undefined1 *)(iVar1 + -3) = 0;
    *(undefined1 *)(iVar1 + -2) = 0;
    if (*(int *)(iVar1 + -0xc) != 0) {
      FUN_0043c0e4(*(undefined4 *)(iVar1 + -0xc),(uint)*(byte *)(iVar1 + -6) << 1,0);
      iVar2 = FUN_004bb07c(param_1 & 0xff);
      if (iVar2 != 0) {
        FUN_0047b488(iVar2,0);
        FUN_0047b48e(iVar2,*(undefined4 *)(iVar1 + -0xc));
      }
    }
    if (*(char *)(iVar1 + -5) == '\x02') {
      *(undefined1 *)(iVar1 + -2) = 1;
    }
    else if ((*(char *)*DAT_0053291c == '\0') || (*(char *)(iVar1 + -4) != '\0')) {
      FUN_00531d60(param_1 & 0xff);
    }
  }
  return CONCAT44(param_2,uVar3);
}

