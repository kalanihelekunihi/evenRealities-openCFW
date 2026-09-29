
void FUN_0043e442(int *param_1)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined1 auStack_128 [16];
  undefined1 auStack_118 [16];
  undefined1 auStack_108 [16];
  undefined1 auStack_f8 [16];
  undefined4 local_e8;
  undefined1 local_d8;
  undefined1 local_bd;
  undefined1 local_a0;
  undefined1 local_8c;
  undefined1 auStack_88 [16];
  undefined4 local_78;
  byte local_3f;
  
  iVar1 = FUN_00450286(param_1);
  iVar2 = *param_1;
  if (iVar1 == 0x1a) {
    pcVar3 = (char *)param_1[4];
    if (*pcVar3 != '\x02') {
      iVar1 = FUN_0043de54(iVar2,0);
      if (iVar1 == 0) {
        uVar4 = FUN_0043de4a(iVar2,0);
        uVar5 = FUN_0043dd72(iVar2,0);
        uVar6 = FUN_0043dd7c(iVar2,0);
        FUN_0043dcc0(auStack_108,iVar2 + 0x14);
        FUN_00450b98(auStack_108,uVar5,uVar6);
        iVar1 = FUN_00450f28(*(undefined4 *)(pcVar3 + 4),auStack_108,uVar4);
        if (iVar1 == 0) {
          *pcVar3 = '\x01';
        }
        else {
          iVar1 = FUN_0043dda8(iVar2,0);
          if (iVar1 < 0xfd) {
            *pcVar3 = '\x01';
          }
          else {
            iVar1 = FUN_0043de6a(iVar2,0);
            if (iVar1 < 0xfd) {
              *pcVar3 = '\x01';
            }
            else {
              iVar1 = FUN_0043ddb4(iVar2,0);
              if ((iVar1 == 0) ||
                 ((iVar1 = FUN_0043ddcc(iVar2,0), 0xfc < iVar1 &&
                  (iVar1 = FUN_0043ddc0(iVar2,0), 0xfc < iVar1)))) {
                iVar1 = FUN_0043ddd8(iVar2,0);
                if (iVar1 != 0) {
                  for (uVar7 = 0; uVar7 < *(byte *)(iVar1 + 10); uVar7 = uVar7 + 1) {
                    if (*(byte *)(uVar7 * 5 + iVar1 + 3) < 0xfd) {
                      *pcVar3 = '\x01';
                      return;
                    }
                  }
                }
                *pcVar3 = '\0';
              }
              else {
                *pcVar3 = '\x01';
              }
            }
          }
        }
      }
      else {
        *pcVar3 = '\x02';
      }
    }
  }
  else if (iVar1 == 0x1d) {
    uVar4 = FUN_00451960(param_1);
    FUN_00451b9c(auStack_88);
    local_78 = uVar4;
    FUN_00452616(iVar2,0,auStack_88);
    iVar1 = FUN_0043de06(iVar2,0);
    if (iVar1 != 0) {
      local_3f = local_3f | 0x20;
    }
    uVar5 = FUN_0043dd72(iVar2,0);
    uVar6 = FUN_0043dd7c(iVar2,0);
    FUN_0043dcc0(auStack_118,iVar2 + 0x14);
    FUN_00450b98(auStack_118,uVar5,uVar6);
    FUN_00451c6e(uVar4,auStack_88,auStack_118);
  }
  else if (iVar1 == 0x20) {
    uVar4 = FUN_00451960(param_1);
    FUN_0043e63e(iVar2,uVar4);
    iVar1 = FUN_0043ddfc(iVar2,0);
    if ((iVar1 != 0) && (iVar1 = FUN_0043de06(iVar2,0), iVar1 != 0)) {
      FUN_00451b9c(auStack_f8);
      local_d8 = 0;
      local_bd = 0;
      local_a0 = 0;
      local_8c = 0;
      local_e8 = uVar4;
      FUN_00452616(iVar2,0,auStack_f8);
      uVar5 = FUN_0043dd72(iVar2,0);
      uVar6 = FUN_0043dd7c(iVar2,0);
      FUN_0043dcc0(auStack_128,iVar2 + 0x14);
      FUN_00450b98(auStack_128,uVar5,uVar6);
      FUN_00451c6e(uVar4,auStack_f8,auStack_128);
    }
  }
  return;
}

