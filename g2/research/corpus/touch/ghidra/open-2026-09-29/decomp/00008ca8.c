
uint Cy_Flash_GetRowNum(uint param_1)

{
  if (0xffff < param_1) {
    param_1 = param_1 + DAT_00008cc0;
  }
  return param_1 >> 7;
}

