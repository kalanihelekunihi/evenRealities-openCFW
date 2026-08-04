static const unsigned char open_cfw_probe_values[4] = {3, 5, 7, 11};

__attribute__((used, noinline))
unsigned int open_cfw_probe_inner(unsigned int value)
{
    return value + 1U;
}

__attribute__((used, noinline))
unsigned int open_cfw_probe_outer(unsigned int index)
{
    return open_cfw_probe_inner(open_cfw_probe_values[index & 3U]);
}
