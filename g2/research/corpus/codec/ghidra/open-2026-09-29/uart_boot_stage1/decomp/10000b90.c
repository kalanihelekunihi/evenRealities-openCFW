
void gx8002_uart_stage1_railc(undefined4 param_1,uint param_2,uint param_3)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;
  int iStack_24;
  int iStack_20;
  uint *puStack_1c;
  uint *puStack_18;
  int *piStack_14;
  int *piStack_10;
  
  iVar2 = gx8002_uart_stage1_pmu_fill_desc(param_1,&iStack_24);
  if (((iVar2 == 0) && (*(byte **)(iStack_24 + 0xc) != (byte *)0x0)) &&
     (uVar5 = (uint)**(byte **)(iStack_24 + 0xc), uVar5 != 0)) {
    puVar6 = (uint *)(uVar5 + iStack_20);
    if ((param_2 != (*puVar6 & 0xffffff)) || (param_3 != (*puVar6 >> 0x1b & 1))) {
      uVar5 = (uint)*(char *)(iStack_24 + 4);
      cVar1 = *(char *)(iStack_24 + 6);
      if ((int)uVar5 < 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = *puStack_18 >> (uVar5 & 0x3f) & 1;
        if (uVar3 != 0) {
          *piStack_10 = 1 << (uVar5 & 0x3f);
        }
      }
      if ((*puStack_1c >> ((int)cVar1 & 0x3fU) & 1) == 0) {
        param_2 = (uint)(byte)~(param_3 != 0) << 0x1b | param_2;
        *puVar6 = 0;
        *puVar6 = 0;
        *puVar6 = 0;
        *puVar6 = param_2;
        *puVar6 = param_2 | 0x6000000;
        *puVar6 = param_2 | 0x6000000;
        *puVar6 = param_2;
      }
      else {
        uVar4 = 1 << ((int)cVar1 & 0x3fU);
        uVar7 = ~uVar4;
        *puStack_1c = *puStack_1c & uVar7;
        param_2 = (uint)(byte)~(param_3 != 0) << 0x1b | param_2;
        *puVar6 = 0;
        *puVar6 = 0;
        *puVar6 = 0;
        *puVar6 = param_2;
        *puVar6 = param_2 | 0x6000000;
        *puVar6 = param_2 | 0x6000000;
        *puVar6 = param_2;
        *puStack_1c = uVar4 | uVar7 & *puStack_1c;
      }
      if (uVar3 != 0) {
        *piStack_14 = 1 << (uVar5 & 0x3f);
      }
    }
  }
  return;
}

