
undefined4 smpSendKey(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  ushort *puVar3;
  int iVar4;
  undefined1 *puVar5;
  undefined4 local_40;
  undefined *local_3c;
  uint local_38;
  uint local_34;
  undefined1 auStack_2c [8];
  undefined2 local_24;
  undefined1 local_22;
  undefined1 local_21;
  undefined4 uStack_1c;
  
  iVar4 = DAT_0056f154;
  uStack_1c = param_4;
  if (((*(char *)(DAT_0056f154 + 0xf8) != '\0') && (**(char **)(param_1 + 0x48) != '\0')) &&
     (*(char *)(param_1 + 0x43) == '\0')) {
    iVar1 = DmConnRole(*(undefined1 *)(param_1 + 0x3d));
    if (iVar1 == 0) {
      local_22 = 2;
    }
    else {
      local_22 = 1;
    }
    local_40 = CONCAT13(local_40._3_1_,0x2f0000);
    local_40 = CONCAT22(local_40._2_2_,(ushort)*(byte *)(param_1 + 0x3d));
    local_21 = smpGetScSecLevel(param_1);
    local_24 = 0;
    FUN_0043c0e4(auStack_2c,8,0);
    FUN_00542a44(&local_3c,*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10);
    DmSmpCbackExec(&local_40);
    *(undefined1 *)(param_1 + 0x43) = 7;
  }
  if (((((param_2 & 0xff) == 0) || (((param_2 & 0xff) == 1 && (*(char *)(param_1 + 0x43) == '\a'))))
      || (((param_2 & 0xff) < 4 && (*(char *)(param_1 + 0x43) == '\t')))) ||
     (*(char *)(param_1 + 0x43) == '\n')) {
    uVar2 = 1;
  }
  else if (*(char *)(param_1 + 0x3c) == '\0') {
    iVar1 = smpMsgAlloc(0x19);
    if (iVar1 != 0) {
      puVar5 = (undefined1 *)(iVar1 + 8);
      if ((*(char *)(param_1 + 0x43) == '\0') && ((int)(param_2 << 0x1f) < 0)) {
        smpGenerateLtk(param_1);
        *puVar5 = 6;
        FUN_00542a44(iVar1 + 9,*(int *)(param_1 + 0x30) + 4);
      }
      else if (*(char *)(param_1 + 0x43) == '\x06') {
        *puVar5 = 7;
        *(char *)(iVar1 + 9) = (char)*(undefined2 *)(*(int *)(param_1 + 0x30) + 0x1c);
        *(char *)(iVar1 + 10) =
             (char)((ushort)*(undefined2 *)(*(int *)(param_1 + 0x30) + 0x1c) >> 8);
        FUN_00439be4(iVar1 + 0xb,*(int *)(param_1 + 0x30) + 0x14,8);
      }
      else if (((int)(param_2 << 0x1e) < 0) &&
              ((*(char *)(param_1 + 0x43) == '\0' || (*(char *)(param_1 + 0x43) == '\a')))) {
        *puVar5 = 8;
        uVar2 = DmSecGetLocalIrk();
        FUN_00542a44(iVar1 + 9,uVar2);
      }
      else if (*(char *)(param_1 + 0x43) == '\b') {
        *puVar5 = 9;
        *(undefined1 *)(iVar1 + 9) = 0;
        uVar2 = HciGetBdAddr();
        FUN_004d293c(iVar1 + 10,uVar2);
      }
      else {
        if ((-1 < (int)(param_2 << 0x1d)) ||
           (((*(char *)(param_1 + 0x43) != '\0' && (*(char *)(param_1 + 0x43) != '\t')) &&
            (*(char *)(param_1 + 0x43) != '\a')))) {
          WsfMsgFree(iVar1);
          iVar4 = FUN_004c9c50();
          if ((iVar4 == 0) || (iVar4 = FUN_0044b610(PTR_DAT_0056f158,&DAT_0056ec88,3), iVar4 != 0))
          {
            iVar4 = FUN_004c9c50();
            if ((iVar4 == 0) ||
               (iVar4 = FUN_0044b610(PTR_DAT_0056f158,PTR_DAT_0056f158,4), iVar4 != 0)) {
              iVar4 = FUN_004c9c50();
              if ((iVar4 == 0) ||
                 (iVar4 = FUN_0044b610(PTR_DAT_0056f158,DAT_0056f168,4), iVar4 != 0)) {
                iVar4 = FUN_004c9c50();
                if (iVar4 == 0) {
                  iVar4 = FUN_004c9c50();
                  if ((iVar4 == 0) ||
                     (iVar4 = FUN_0044b610(&DAT_0056ec8c,&DAT_0056ec90,3), iVar4 != 0)) {
                    WsfTrace(PTR_DAT_0056f158,PTR_s_smpSendKey_unexpected_state_keyD_0056f15c,
                             param_2 & 0xff,*(undefined1 *)(param_1 + 0x43));
                  }
                }
                else {
                  iVar4 = FUN_0043d0ce();
                  if (iVar4 << 0x1e < 0) {
                    local_34 = (uint)*(byte *)(param_1 + 0x43);
                    local_38 = param_2 & 0xff;
                    local_3c = PTR_s_smpSendKey_unexpected_state_keyD_0056f15c;
                    local_40 = 0x24a;
                    FUN_0043d574(4,&DAT_0056ec8c,DAT_0056f164,PTR_s_smpSendKey_0056f160);
                  }
                }
              }
              else {
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  local_34 = (uint)*(byte *)(param_1 + 0x43);
                  local_38 = param_2 & 0xff;
                  local_3c = PTR_s_smpSendKey_unexpected_state_keyD_0056f15c;
                  local_40 = 0x24a;
                  FUN_0043d574(3,&DAT_0056ec8c,DAT_0056f164,PTR_s_smpSendKey_0056f160);
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_34 = (uint)*(byte *)(param_1 + 0x43);
                local_38 = param_2 & 0xff;
                local_3c = PTR_s_smpSendKey_unexpected_state_keyD_0056f15c;
                local_40 = 0x24a;
                FUN_0043d574(2,&DAT_0056ec8c,DAT_0056f164,PTR_s_smpSendKey_0056f160);
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_34 = (uint)*(byte *)(param_1 + 0x43);
              local_38 = param_2 & 0xff;
              local_3c = PTR_s_smpSendKey_unexpected_state_keyD_0056f15c;
              local_40 = 0x24a;
              FUN_0043d574(1,&DAT_0056ec8c,DAT_0056f164,PTR_s_smpSendKey_0056f160);
            }
          }
          return 1;
        }
        *puVar5 = 10;
        uVar2 = DmSecGetLocalCsrk();
        FUN_00542a44(iVar1 + 9,uVar2);
      }
      *(undefined1 *)(param_1 + 0x43) = *(undefined1 *)(iVar1 + 8);
      smpSendPkt(param_1,iVar1);
      if ((*(char *)(param_1 + 0x3c) == '\0') &&
         (puVar3 = (ushort *)WsfMsgAlloc(4), puVar3 != (ushort *)0x0)) {
        *(undefined1 *)(puVar3 + 1) = 0xc;
        *puVar3 = (ushort)*(byte *)(param_1 + 0x3d);
        WsfMsgSend(*(undefined1 *)(iVar4 + 0xec),puVar3);
      }
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

