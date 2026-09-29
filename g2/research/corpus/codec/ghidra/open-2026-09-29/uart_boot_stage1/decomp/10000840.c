
void gx8002_uart_stage1_pmu_bit_modify(uint *param_1)

{
  uint uVar1;
  
  uVar1 = *param_1 & 0x3f;
  uRam0000008c = (-2 << uVar1 | 0xfffffffeU >> 0x20 - uVar1) & uRam0000008c |
                 (uint)(byte)param_1[1] << (*param_1 & 0x3f);
  return;
}

