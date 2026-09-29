
bool cJSON_IsArray(int param_1)

{
  bool bVar1;
  
  if (param_1 == 0) {
    bVar1 = false;
  }
  else {
    bVar1 = *(char *)(param_1 + 0xc) == ' ';
  }
  return bVar1;
}

