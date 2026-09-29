
undefined8 l2cRxSignalingPkt(undefined2 param_1,uint param_2,undefined *param_3)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  undefined *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_3;
  if ((3 < (param_2 & 0xffff)) && (cVar1 = DmConnIdByHandle(param_1), cVar1 != '\0')) {
    cVar1 = DmConnRole(cVar1);
    if ((cVar1 == '\0') && (*(int *)(DAT_00530b90 + 0x18) != 0)) {
      (**(code **)(DAT_00530b90 + 0x18))(param_1,param_2 & 0xffff,param_3);
    }
    else if ((cVar1 == '\x01') && (*(int *)(DAT_00530b90 + 0x1c) != 0)) {
      (**(code **)(DAT_00530b90 + 0x1c))(param_1,param_2 & 0xffff,param_3);
    }
    else {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530a9c,&DAT_00530a9c,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530a9c,PTR_DAT_00530b74,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530a9c,PTR_DAT_00530b84,4), iVar2 != 0))
          {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530aa0,&DAT_00530adc,3), iVar2 != 0))
              {
                WsfTrace(&DAT_00530a9c,PTR_s_Invalid_role_configuration__role_00530b94,cVar1);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                uVar3 = 0x80;
                puVar4 = PTR_s_Invalid_role_configuration__role_00530b94;
                FUN_0043d574(4,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                             PTR_s_l2cRxSignalingPkt_00530b98,0x80,
                             PTR_s_Invalid_role_configuration__role_00530b94,cVar1);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              uVar3 = 0x80;
              puVar4 = PTR_s_Invalid_role_configuration__role_00530b94;
              FUN_0043d574(3,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                           PTR_s_l2cRxSignalingPkt_00530b98,0x80,
                           PTR_s_Invalid_role_configuration__role_00530b94,cVar1);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar3 = 0x80;
            puVar4 = PTR_s_Invalid_role_configuration__role_00530b94;
            FUN_0043d574(2,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                         PTR_s_l2cRxSignalingPkt_00530b98,0x80,
                         PTR_s_Invalid_role_configuration__role_00530b94,cVar1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = 0x80;
          puVar4 = PTR_s_Invalid_role_configuration__role_00530b94;
          FUN_0043d574(1,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                       PTR_s_l2cRxSignalingPkt_00530b98,0x80,
                       PTR_s_Invalid_role_configuration__role_00530b94,cVar1);
        }
      }
    }
  }
  return CONCAT44(puVar4,uVar3);
}

