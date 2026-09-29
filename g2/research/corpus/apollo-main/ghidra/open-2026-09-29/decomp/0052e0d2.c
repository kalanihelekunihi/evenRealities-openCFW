
int FUN_0052e0d2(undefined4 *param_1,int param_2,uint param_3)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 local_168 [4];
  uint local_158;
  undefined1 local_154;
  undefined1 *local_150;
  undefined1 *local_14c;
  undefined1 local_148;
  undefined1 local_147;
  undefined4 local_144;
  undefined4 local_140;
  undefined1 auStack_138 [16];
  undefined1 local_128 [260];
  
  iVar3 = FUN_0052e072(param_1);
  if (iVar3 == 0) {
    if (param_3 < 0x104) {
      uVar6 = 0;
      while (uVar6 < param_3) {
        bVar2 = FUN_0052df50(param_1);
        if (bVar2 == 0) {
          iVar3 = 8;
          FUN_0052e058(param_1);
          break;
        }
        if ((uint)bVar2 < param_3 - uVar6) {
          uVar5 = (uint)bVar2;
        }
        else {
          uVar5 = param_3 - uVar6;
        }
        if ((uVar5 != 0) && (bVar2 != 0)) {
          FUN_00439be4(local_128,param_2 + uVar6,uVar5);
          uVar6 = uVar5 + uVar6;
          iVar4 = FUN_0052dd1c();
          if (iVar4 == 0) {
            FUN_0043c0e4(local_168,0x30,0);
            local_154 = 2;
            local_150 = local_128;
            local_14c = auStack_138;
            local_148 = 0;
            local_147 = 0;
            local_144 = 0;
            local_140 = 0;
            local_168[0] = 0;
            local_158 = uVar5;
            cVar1 = FUN_0055cf40(param_1[1],local_168);
            if (cVar1 != '\0') {
              iVar3 = 0xb;
              FUN_004733ee(DAT_0052ed30,cVar1,*param_1);
            }
          }
          else {
            for (bVar2 = 0; bVar2 < uVar5; bVar2 = bVar2 + 1) {
              FUN_0052dc98(local_128[bVar2]);
            }
          }
        }
        FUN_0052e058(param_1);
      }
    }
    else {
      iVar3 = 9;
      FUN_004733ee(DAT_0052ede0);
    }
    FUN_0052e0a2(param_1);
  }
  return iVar3;
}

