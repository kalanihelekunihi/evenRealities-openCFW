
void FUN_00531bd4(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,&DAT_00531d58,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532624,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00532624,DAT_00532634,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00531d5c,&DAT_00531f14,3), iVar1 != 0)) {
              WsfTrace(DAT_00532624,DAT_00532628,0,param_2);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_00531d5c,DAT_00532630,DAT_0053262c,0x5d,DAT_00532628,0,param_2);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_00531d5c,DAT_00532630,DAT_0053262c,0x5d,DAT_00532628,0,param_2);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_00531d5c,DAT_00532630,DAT_0053262c,0x5d,DAT_00532628,0,param_2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_00531d5c,DAT_00532630,DAT_0053262c,0x5d,DAT_00532628,0,param_2,param_4);
      }
    }
  }
  else if (param_2 < 8) {
    (*(code *)*DAT_0053290c)(param_1,6);
  }
  else if ((param_2 == 8) && (*(char *)(DAT_00532638 + (uint)param_1 * 0x10 + -8) == '\0')) {
    (*(code *)*DAT_0053290c)(param_1,7);
  }
  return;
}

