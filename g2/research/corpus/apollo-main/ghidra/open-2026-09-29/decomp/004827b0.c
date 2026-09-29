
undefined8 FUN_004827b0(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 local_18;
  
  iVar2 = FUN_00482708(param_1);
  if (iVar2 == 0) {
    local_18 = param_4;
    if ((char)param_1[2] == '\0') {
      uVar3 = 0;
    }
    else {
      iVar2 = *param_1 + (uint)*(byte *)(param_1 + 2) * 4;
      for (uVar4 = 0; uVar4 < *(byte *)(param_1 + 2); uVar4 = uVar4 + 1) {
        if (*(char *)(iVar2 + uVar4) == param_2) {
          iVar7 = *param_1;
          iVar5 = FUN_0044f718((*(byte *)(param_1 + 2) - 1) * 5);
          if (iVar5 == 0) {
            uVar3 = 0;
          }
          else {
            *param_1 = iVar5;
            *(char *)(param_1 + 2) = (char)param_1[2] + -1;
            bVar1 = *(byte *)(param_1 + 2);
            iVar6 = 0;
            for (uVar4 = 0; uVar4 <= *(byte *)(param_1 + 2); uVar4 = uVar4 + 1) {
              if (*(char *)(iVar2 + uVar4) != param_2) {
                *(undefined4 *)(iVar5 + iVar6 * 4) = *(undefined4 *)(iVar7 + uVar4 * 4);
                *(undefined1 *)(iVar5 + (uint)bVar1 * 4 + iVar6) = *(undefined1 *)(iVar2 + uVar4);
                iVar6 = iVar6 + 1;
              }
            }
            FUN_0044f758(iVar7);
            uVar3 = 1;
          }
          goto LAB_00482866;
        }
      }
      uVar3 = 0;
    }
  }
  else {
    local_18 = DAT_00482abc;
    FUN_0044d25c(3,DAT_00482ab4,0x117,DAT_00482ac0);
    uVar3 = 0;
  }
LAB_00482866:
  return CONCAT44(local_18,uVar3);
}

