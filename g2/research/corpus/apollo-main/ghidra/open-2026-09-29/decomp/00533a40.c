
undefined8 attsIndConnCback(int param_1,int param_2,undefined *param_3)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  
  if ((*(char *)(param_2 + 2) != '\'') && (*(char *)(param_2 + 2) == '(')) {
    if (*(char *)(param_2 + 3) == '\0') {
      cVar1 = *(char *)(param_2 + 8);
    }
    else {
      cVar1 = *(char *)(param_2 + 3);
    }
    for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
      if (*(char *)(param_1 + 0xe) == '\0') {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533e9c,&DAT_00533bc8,3), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533e9c,DAT_00533e9c,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533e9c,DAT_00533eac,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if (iVar2 == 0) {
                iVar2 = FUN_004c9c50();
                if ((iVar2 == 0) ||
                   (iVar2 = FUN_0044b610(&LAB_00533dd4,&DAT_00533e90,3), iVar2 != 0)) {
                  WsfTrace(DAT_00533e9c,PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0,
                           *(undefined1 *)(param_1 + 0xe));
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  param_2 = 0x115;
                  param_3 = PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0;
                  FUN_0043d574(4,&LAB_00533dd4,PTR_s_D__01_workspace_s200_ap510b_iar__00533ea8,
                               PTR_s_attsIndConnCback_00533ea4,0x115,
                               PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0,
                               *(undefined1 *)(param_1 + 0xe));
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                param_2 = 0x115;
                param_3 = PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0;
                FUN_0043d574(3,&LAB_00533dd4,PTR_s_D__01_workspace_s200_ap510b_iar__00533ea8,
                             PTR_s_attsIndConnCback_00533ea4,0x115,
                             PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0,
                             *(undefined1 *)(param_1 + 0xe));
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              param_2 = 0x115;
              param_3 = PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0;
              FUN_0043d574(2,&LAB_00533dd4,PTR_s_D__01_workspace_s200_ap510b_iar__00533ea8,
                           PTR_s_attsIndConnCback_00533ea4,0x115,
                           PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0,
                           *(undefined1 *)(param_1 + 0xe));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x115;
            param_3 = PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0;
            FUN_0043d574(1,&LAB_00533dd4,PTR_s_D__01_workspace_s200_ap510b_iar__00533ea8,
                         PTR_s_attsIndConnCback_00533ea4,0x115,
                         PTR_s_Invalid_pCcb_>connId_in_AttsIndC_00533ea0,
                         *(undefined1 *)(param_1 + 0xe));
          }
        }
        break;
      }
      iVar2 = DAT_00533e98 + (uint)*(byte *)(param_1 + 0xe) * 0xc0 + (uint)bVar3 * 0x40;
      if (*(short *)(iVar2 + -0x9a) != 0) {
        WsfTimerStop(iVar2 + -0xc0);
        *(undefined2 *)(iVar2 + -0x9a) = 0;
      }
      attsIndNtfCallback(*(undefined1 *)(param_1 + 0xe),iVar2 + -0xc0,cVar1 + -0x60);
    }
  }
  return CONCAT44(param_3,param_2);
}

