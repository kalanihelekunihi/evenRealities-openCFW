# Independent review 2289

**Result:** PASS_SCOPED.

Isolated replay regenerated all 2,592 fixtures. Source, body [0x7BC0,0x7CEE), literal range [0x7CF0,0x7CF8), and artifact hashes match. Independent decode confirms the saved child-status slot return at 7C02, allowing the type-7 source pointer to use the saved slot even if 6AC0 clobbers R1. The mode failure still proceeds to measurement processing; mode success calls start, budget and poll in order, with poll timeout ORed into retained status. Measurement/status reloads, bit-31 clear, baseline exceptions, wraparound delta scaling, unsigned saturation, minimum-one result and high-register/SP assertions match the tested cases.

**Limits:** All children are controlled in this candidate and mode/type/measurement inputs are a bounded grid. Hardware samples/status and register meaning are modeled; pointer aliasing/mutation, untested mode transitions and physical behavior remain open. No canonical admission.
