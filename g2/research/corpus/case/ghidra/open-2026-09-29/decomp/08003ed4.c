
void case_flash_control_update(uint param_1,uint param_2,uint param_3)

{
  *(uint *)(DAT_08003ee8 + 0x20) =
       *(uint *)(DAT_08003ee8 + 0x20) & ~(param_1 | 0xff) | param_2 | param_3;
  return;
}

