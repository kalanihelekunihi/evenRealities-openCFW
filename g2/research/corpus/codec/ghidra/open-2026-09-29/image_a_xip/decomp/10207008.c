
byte LvpQueueIsFull(int *param_1)

{
  return ~((*param_1 + param_1[4]) - param_1[3] * ((*param_1 + param_1[4]) / param_1[3]) !=
          param_1[1]);
}

