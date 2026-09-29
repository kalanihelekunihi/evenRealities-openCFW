
undefined4 FUN_005dec90(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  uint uVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  undefined1 *local_e0;
  int *local_d8;
  uint local_d0;
  undefined4 local_cc;
  int local_c8;
  uint local_c4;
  int local_c0 [2];
  undefined2 local_b8;
  undefined2 local_b6;
  undefined1 auStack_b0 [140];
  int local_24;
  uint local_20;
  
  puVar6 = *(undefined1 **)(param_1 + 0x1fc);
  puVar7 = puVar6 + *(int *)(param_1 + 0x200);
  if ((puVar6 == (undefined1 *)0x0) || (puVar7 < puVar6 + 4)) {
    uVar1 = 8;
  }
  else if (CONCAT11(*puVar6,puVar6[1]) == 0) {
    local_d0 = (uint)CONCAT11(puVar6[2],puVar6[3]);
    local_e0 = puVar6 + 4;
    while ((local_d0 != 0 && (local_e0 + 8 <= puVar7))) {
      local_b8 = CONCAT11(*local_e0,local_e0[1]);
      local_b6 = CONCAT11(local_e0[2],local_e0[3]);
      local_c0[1] = 0;
      uVar5 = (uint)(byte)local_e0[7] |
              (uint)(byte)local_e0[5] << 0x10 | (uint)(byte)local_e0[4] << 0x18 |
              (uint)(byte)local_e0[6] << 8;
      if ((uVar5 != 0) && (uVar5 <= *(int *)(param_1 + 0x200) - 2U)) {
        puVar4 = puVar6 + uVar5;
        local_c4 = (uint)CONCAT11(*puVar4,puVar4[1]);
        for (local_d8 = DAT_005dfa08; *local_d8 != 0; local_d8 = local_d8 + 1) {
          iVar2 = *local_d8;
          if (*(uint *)(iVar2 + 0x28) == local_c4) {
            local_cc = 0;
            local_c0[0] = param_1;
            ft_validator_init(auStack_b0,puVar4,puVar7,0);
            local_20 = (uint)*(ushort *)(param_1 + 0x108);
            iVar3 = FUN_0056777c(auStack_b0);
            if (iVar3 == 0) {
              local_cc = (**(code **)(iVar2 + 0x2c))(puVar4,auStack_b0);
            }
            if ((local_24 == 0) &&
               (iVar2 = FT_CMap_New(iVar2,puVar4,local_c0,&local_c8), iVar2 == 0)) {
              *(undefined4 *)(local_c8 + 0x14) = local_cc;
            }
            break;
          }
        }
      }
      local_d0 = local_d0 - 1;
      local_e0 = local_e0 + 8;
    }
    uVar1 = 0;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}

