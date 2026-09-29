
undefined8 FUN_00531d60(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,&DAT_00531f18,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532624,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532634,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00531f1c,&DAT_00531f14,3), iVar1 != 0)) {
              WsfTrace(DAT_00532624,DAT_0053263c,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x7c;
              param_3 = DAT_0053263c;
              FUN_0043d574(4,&DAT_00531f1c,DAT_00532630,DAT_00532640,0x7c,DAT_0053263c,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x7c;
            param_3 = DAT_0053263c;
            FUN_0043d574(3,&DAT_00531f1c,DAT_00532630,DAT_00532640,0x7c,DAT_0053263c,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x7c;
          param_3 = DAT_0053263c;
          FUN_0043d574(2,&DAT_00531f1c,DAT_00532630,DAT_00532640,0x7c,DAT_0053263c,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x7c;
        param_3 = DAT_0053263c;
        FUN_0043d574(1,&DAT_00531f1c,DAT_00532630,DAT_00532640,0x7c,DAT_0053263c,0);
      }
    }
  }
  else {
    iVar1 = DAT_00532638 + (uint)param_1 * 0x10;
    if (*(char *)(iVar1 + -5) == '\0') {
      iVar2 = FUN_004bb07c(param_1);
      if (iVar2 == 0) {
        bVar3 = *(byte *)(iVar1 + -7);
      }
      else {
        bVar3 = 0;
      }
      if (bVar3 < 4) {
        (*(code *)*DAT_0053290c)(param_1,3);
      }
      else if (bVar3 != 5) {
        if ((iVar2 != 0) && (*(int *)(iVar1 + -0xc) != 0)) {
          if (*(char *)(iVar2 + 0x86) != '\0') {
            FUN_005336e0(param_1);
            goto LAB_00531f10;
          }
          FUN_00439be4(*(undefined4 *)(iVar1 + -0xc),iVar2 + 0x98,(uint)*(byte *)(iVar1 + -6) << 1);
        }
        FUN_00531bd4(param_1,bVar3);
      }
    }
  }
LAB_00531f10:
  return CONCAT44(param_3,param_2);
}

