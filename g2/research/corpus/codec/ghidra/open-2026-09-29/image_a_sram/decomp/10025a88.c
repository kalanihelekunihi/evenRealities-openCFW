
void gx8002_clock_init_pointer(void)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int aiStack_2c [2];
  undefined1 auStack_24 [12];
  
  gx8002_clock_module_divider_set(6,1);
  iVar3 = gx8002_start_mode();
  if (iVar3 == 0) {
    iVar4 = gx8002_trim_state();
    iVar9 = iRam10025ca4;
    iVar8 = iRam10025c9c;
    if (iVar4 == 1) {
      *(undefined4 *)(iRam10025c9c + 0x38) = 1;
      iVar4 = *(int *)(iVar8 + 0x14);
      gx8002_memcpy(aiStack_2c,uRam10025ca0,0x14);
      iVar9 = 0;
      while( true ) {
        *(int *)(iVar8 + 0x14) = aiStack_2c[iVar9] + iVar4;
        iVar5 = gx8002_clock_pll_wait_timeout(iVar8,0x28);
        iVar2 = iRam10025cb0;
        if (iVar5 == 0) break;
        iVar9 = iVar9 + 1;
        if (iVar9 == 5) {
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
      }
      iVar8 = 0;
      do {
        iVar9 = iVar2 + iVar8;
        iVar8 = iVar8 + 8;
        gx8002_clock_source_select(iVar9);
      } while (iVar8 != 0x50);
    }
    else {
      iVar8 = 0;
      do {
        iVar4 = iVar9 + iVar8;
        iVar8 = iVar8 + 8;
        gx8002_clock_source_select(iVar4);
      } while (iVar8 != 0x50);
    }
  }
  else if (iVar3 == 1) {
    gx8002_memcpy(aiStack_2c,uRam10025ca8,0x10);
    if (*(int *)(iRam10025c9c + 0x38) == 1) {
      gx8002_clock_pll_wait();
    }
    gx8002_clock_source_select(aiStack_2c);
    gx8002_clock_source_select(auStack_24);
  }
  gx8002_clock_module_source_fixed(10,1);
  gx8002_clock_module_source_fixed(6,1);
  gx8002_clock_module_source_fixed(0,2);
  gx8002_clock_module_source_fixed(1,0);
  gx8002_clock_module_source_fixed(3,0);
  gx8002_clock_module_source_fixed(4,0);
  gx8002_clock_module_source_fixed(5,0);
  gx8002_clock_module_source_fixed(2,1);
  gx8002_clock_module_source_fixed(7,3);
  gx8002_clock_module_source_fixed(8,6);
  gx8002_clock_module_source_fixed(9,0);
  gx8002_clock_module_source_fixed(0x16,0);
  gx8002_clock_module_source_fixed(0x10,1);
  gx8002_clock_module_source_fixed(0xb,1);
  gx8002_clock_module_source_fixed(0x13,1);
  gx8002_clock_module_source_fixed(0xc,1);
  gx8002_clock_module_source_fixed(0xd,1);
  gx8002_clock_module_source_fixed(0xe,1);
  gx8002_clock_module_source_fixed(0xf,1);
  gx8002_clock_module_dto_set(2,0x1000000,0);
  gx8002_clock_module_divider_set(6,1);
  gx8002_clock_module_divider_set(0,4);
  gx8002_clock_module_divider_set(1,3);
  gx8002_clock_module_divider_set(3,2);
  gx8002_clock_module_divider_set(2);
  gx8002_clock_module_divider_set(7,0x180);
  gx8002_clock_module_divider_set(8,0xc);
  gx8002_clock_module_divider_set(0x13,2);
  gx8002_clock_module_dto_set(0x10,0x1000000,0);
  gx8002_clock_module_dto_set(0xb,0x1000000,1);
  gx8002_clock_module_divider_set(10,3);
  gx8002_clock_module_divider_set(0xc,1);
  gx8002_clock_module_divider_set(0xd,1);
  gx8002_clock_module_divider_set(0xf,2);
  gx8002_clock_module_divider_set(0xe,2);
  puVar1 = puRam10025cac;
  if (iVar3 == 1) {
    uVar6 = 0xb;
    do {
      uVar7 = uVar6 + 1;
      gx8002_platform_gate(uVar6,*puVar1 >> (uVar6 & 0x3f) & 1);
      uVar6 = uVar7;
    } while (uVar7 != 0x1a);
  }
  gx8002_platform_gate(5,1);
  *(uint *)(iRam10025cb4 + 4) = *(uint *)(iRam10025cb4 + 4) & 0xfffffffe;
  iVar3 = iRam10025cb8;
  *(uint *)(iRam10025cb8 + 0x60) = *(uint *)(iRam10025cb8 + 0x60) & 0xfffffffd;
  *(undefined4 *)(iVar3 + 0x40) = 0x59;
  *(undefined4 *)(iVar3 + 0x44) = 0x59;
  *(undefined4 *)(iVar3 + 0x48) = 0x59;
  *(undefined4 *)(iVar3 + 0x4c) = 0x59;
  gx_analog_set_ldo_ana_voltage(0);
  gx8002_digital_voltage(0);
  return;
}

