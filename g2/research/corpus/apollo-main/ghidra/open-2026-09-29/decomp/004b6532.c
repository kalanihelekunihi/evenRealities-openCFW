
undefined8 dmConnUpdExecute(int param_1,undefined *param_2)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  
  iVar3 = param_1;
  puVar4 = param_2;
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,&DAT_004b67d4,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,DAT_004b67d0,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,DAT_004b67cc,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b67d8,&DAT_004b6880,3), iVar2 != 0)) {
            WsfTrace(DAT_004b67cc,DAT_004b6f24,param_2[2],*(undefined1 *)(param_1 + 0x15));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            iVar3 = 0x271;
            puVar4 = DAT_004b6f24;
            FUN_0043d574(4,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x271,
                         DAT_004b6f24,param_2[2],*(undefined1 *)(param_1 + 0x15));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar3 = 0x271;
          puVar4 = DAT_004b6f24;
          FUN_0043d574(3,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x271,
                       DAT_004b6f24,param_2[2],*(undefined1 *)(param_1 + 0x15));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar3 = 0x271;
        puVar4 = DAT_004b6f24;
        FUN_0043d574(2,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x271,DAT_004b6f24
                     ,param_2[2],*(undefined1 *)(param_1 + 0x15));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar3 = 0x271;
      puVar4 = DAT_004b6f24;
      FUN_0043d574(1,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x271,DAT_004b6f24,
                   param_2[2],*(undefined1 *)(param_1 + 0x15));
    }
  }
  bVar1 = PTR_DAT_004b7074[(byte)param_2[2] & 7];
  if (bVar1 >> 4 < 3) {
    iVar2 = *(int *)(DAT_004b71d0 + ((int)(uint)bVar1 >> 4) * 4);
    if (iVar2 != 0) {
      (**(code **)(iVar2 + (bVar1 & 0xf) * 4))(param_1,param_2);
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b67d4,&DAT_004b67d4,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b67d4,DAT_004b67d0,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b67d4,DAT_004b67cc,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b67d8,&DAT_004b6880,3), iVar2 != 0)) {
              WsfTrace(&DAT_004b67d4,PTR_s_dmConnUpdExecute__Invalid_action_004b7078,bVar1 >> 4);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar3 = 0x279;
              puVar4 = PTR_s_dmConnUpdExecute__Invalid_action_004b7078;
              FUN_0043d574(4,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x279,
                           PTR_s_dmConnUpdExecute__Invalid_action_004b7078,bVar1 >> 4);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            iVar3 = 0x279;
            puVar4 = PTR_s_dmConnUpdExecute__Invalid_action_004b7078;
            FUN_0043d574(3,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x279,
                         PTR_s_dmConnUpdExecute__Invalid_action_004b7078,bVar1 >> 4);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar3 = 0x279;
          puVar4 = PTR_s_dmConnUpdExecute__Invalid_action_004b7078;
          FUN_0043d574(2,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x279,
                       PTR_s_dmConnUpdExecute__Invalid_action_004b7078,bVar1 >> 4);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar3 = 0x279;
        puVar4 = PTR_s_dmConnUpdExecute__Invalid_action_004b7078;
        FUN_0043d574(1,&DAT_004b67d8,DAT_004b67e8,PTR_s_dmConnUpdExecute_004b7070,0x279,
                     PTR_s_dmConnUpdExecute__Invalid_action_004b7078,bVar1 >> 4);
      }
    }
  }
  return CONCAT44(puVar4,iVar3);
}

