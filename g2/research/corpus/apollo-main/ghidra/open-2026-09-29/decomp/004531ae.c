
void FUN_004531ae(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined1 *puVar7;
  uint uVar8;
  undefined1 auStack_130 [4];
  int local_12c;
  int local_124;
  undefined1 auStack_120 [4];
  int local_11c;
  int local_114;
  undefined1 auStack_110 [4];
  int local_10c;
  int local_104;
  undefined1 auStack_100 [16];
  undefined1 auStack_f0 [16];
  undefined1 auStack_e0 [16];
  undefined1 auStack_d0 [16];
  undefined1 auStack_c0 [28];
  undefined4 local_a4;
  undefined1 auStack_54 [28];
  undefined1 auStack_38 [16];
  int local_28;
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  FUN_00439c04(auStack_100,param_1 + 0x18,0x10);
  FUN_0043fc2a(param_2,auStack_f0);
  uVar2 = FUN_00452dc8(param_2);
  FUN_00450b98(auStack_f0,uVar2);
  iVar3 = FUN_00450bcc(auStack_e0,auStack_100,auStack_f0);
  if (iVar3 != 0) {
    FUN_00439c04(param_1 + 0x18,auStack_e0,0x10);
    FUN_00451670(param_2,0x1c,param_1);
    FUN_00451670(param_2,0x1d,param_1);
    FUN_00451670(param_2,0x1e,param_1);
    iVar3 = FUN_0043e0e0(param_2,0x100000);
    if (iVar3 == 0) {
      puVar7 = (undefined1 *)(param_2 + 0x14);
    }
    else {
      puVar7 = auStack_f0;
    }
    iVar3 = FUN_00450bcc(auStack_d0,auStack_100,puVar7);
    if (iVar3 != 0) {
      uVar4 = FUN_0044ddea(param_2);
      if (uVar4 == 0) {
        FUN_00439c04(param_1 + 0x18,auStack_e0,0x10);
        FUN_00451670(param_2,0x1f,param_1);
        FUN_00451670(param_2,0x20,param_1);
        FUN_00451670(param_2,0x21,param_1);
      }
      else {
        FUN_00439c04(param_1 + 0x18,auStack_d0,0x10);
        cVar1 = FUN_0045316a(param_2,0);
        iVar3 = 0;
        if ((cVar1 != '\0') && (iVar3 = FUN_00453160(param_2,0), iVar3 == 0)) {
          cVar1 = '\0';
        }
        if (cVar1 == '\0') {
          for (uVar8 = 0; uVar8 < uVar4; uVar8 = uVar8 + 1) {
            FUN_004541b6(param_1,*(undefined4 *)(**(int **)(param_2 + 8) + uVar8 * 4));
          }
          FUN_00439c04(param_1 + 0x18,auStack_e0,0x10);
          FUN_00451670(param_2,0x1f,param_1);
          FUN_00451670(param_2,0x20,param_1);
          FUN_00451670(param_2,0x21,param_1);
        }
        else {
          FUN_0048a984(auStack_54);
          local_28 = iVar3;
          FUN_00439c04(auStack_38,param_2 + 0x14,0x10);
          FUN_00488918(auStack_c0);
          iVar5 = FUN_00451598(param_2 + 0x14);
          iVar6 = FUN_004515a4(param_2 + 0x14);
          if (iVar5 < iVar6) {
            iVar5 = FUN_00451598(param_2 + 0x14);
          }
          else {
            iVar5 = FUN_004515a4(param_2 + 0x14);
          }
          if (iVar5 >> 1 <= iVar3) {
            iVar3 = iVar5 >> 1;
          }
          FUN_00439c04(auStack_110,param_2 + 0x14,0x10);
          local_10c = (local_104 - iVar3) + 1;
          iVar5 = FUN_00450bcc(auStack_110,auStack_110,auStack_100);
          if (iVar5 != 0) {
            uVar2 = FUN_0048475e(param_1,0x10,auStack_110);
            for (uVar8 = 0; uVar8 < uVar4; uVar8 = uVar8 + 1) {
              FUN_004541b6(uVar2,*(undefined4 *)(**(int **)(param_2 + 8) + uVar8 * 4));
            }
            FUN_00451670(param_2,0x1f,uVar2);
            FUN_00451670(param_2,0x20,uVar2);
            FUN_00451670(param_2,0x21,uVar2);
            FUN_0048a98e(uVar2,auStack_54);
            local_a4 = uVar2;
            FUN_0048895e(param_1,auStack_c0,auStack_110);
          }
          FUN_00439c04(auStack_120,param_2 + 0x14,0x10);
          local_114 = iVar3 + local_11c + -1;
          iVar5 = FUN_00450bcc(auStack_120,auStack_120,auStack_100);
          if (iVar5 != 0) {
            uVar2 = FUN_0048475e(param_1,0x10,auStack_120);
            for (uVar8 = 0; uVar8 < uVar4; uVar8 = uVar8 + 1) {
              FUN_004541b6(uVar2,*(undefined4 *)(**(int **)(param_2 + 8) + uVar8 * 4));
            }
            FUN_00451670(param_2,0x1f,uVar2);
            FUN_00451670(param_2,0x20,uVar2);
            FUN_00451670(param_2,0x21,uVar2);
            FUN_0048a98e(uVar2,auStack_54);
            local_a4 = uVar2;
            FUN_0048895e(param_1,auStack_c0,auStack_120);
          }
          FUN_00439c04(auStack_130,param_2 + 0x14,0x10);
          local_12c = iVar3 + local_12c;
          local_124 = local_124 - iVar3;
          iVar3 = FUN_00450bcc(auStack_130,auStack_130,auStack_100);
          if (iVar3 != 0) {
            FUN_00439c04(param_1 + 0x18,auStack_130,0x10);
            for (uVar8 = 0; uVar8 < uVar4; uVar8 = uVar8 + 1) {
              FUN_004541b6(param_1,*(undefined4 *)(**(int **)(param_2 + 8) + uVar8 * 4));
            }
            FUN_00451670(param_2,0x1f,param_1);
            FUN_00451670(param_2,0x20,param_1);
            FUN_00451670(param_2,0x21,param_1);
          }
        }
      }
    }
    FUN_00439c04(param_1 + 0x18,auStack_100,0x10);
  }
  return;
}

