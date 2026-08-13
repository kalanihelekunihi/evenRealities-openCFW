static volatile unsigned int open_cfw_implicit_state;

__attribute__((used, noinline))
unsigned int open_cfw_writable_probe(void)
{
    return ++open_cfw_implicit_state;
}
