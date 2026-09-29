
void gx8002_clock_module_dto_set(undefined4 param_1,uint param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iStack_3c;
  int iStack_38;
  uint *puStack_34;
  uint *puStack_30;
  int *piStack_2c;
  int *piStack_28;
  
  iVar1 = __module_get_info(param_1,&iStack_3c);
  if (iVar1 == 0) {
    if ((*(byte **)(iStack_3c + 0xc) != (byte *)0x0) &&
       (uVar3 = (uint)**(byte **)(iStack_3c + 0xc), uVar3 != 0)) {
      puVar4 = (uint *)(uVar3 + iStack_38);
      if ((param_2 != (*puVar4 & 0xffffff)) || (param_3 != ((*puVar4 ^ 0x8000000) >> 0x1b & 1))) {
        uVar3 = (uint)*(char *)(iStack_3c + 4);
        uVar7 = (uint)*(char *)(iStack_3c + 6);
        if ((int)uVar3 < 0) {
          uVar5 = 0;
        }
        else {
          uVar5 = *puStack_30 >> (uVar3 & 0x3f) & 1;
          if (uVar5 != 0) {
            *piStack_28 = 1 << (uVar3 & 0x3f);
          }
        }
        uVar6 = *puStack_34 >> (uVar7 & 0x3f) & 1;
        if (uVar6 != 0) {
          __reg_set_val(puStack_34,uVar7,0,1);
        }
        param_2 = (uint)(byte)~(param_3 != 0) << 0x1b | param_2;
        *puVar4 = 0x4000000;
        *puVar4 = 0;
        *puVar4 = 0x4000000;
        uVar2 = param_2 | 0x4000000;
        param_2 = param_2 | 0x6000000;
        *puVar4 = uVar2;
        *puVar4 = param_2;
        *puVar4 = param_2;
        *puVar4 = uVar2;
        if (uVar6 != 0) {
          __reg_set_val(puStack_34,uVar7,1);
        }
        if (uVar5 != 0) {
          *piStack_2c = 1 << (uVar3 & 0x3f);
        }
      }
    }
  }
  return;
}

