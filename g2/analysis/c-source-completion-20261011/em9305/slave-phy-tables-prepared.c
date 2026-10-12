/* Native six-state/seven-action slave PHY tables, typed relocations. */
extern uint32_t opencfw_em9305_phy_action_31592c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315a28(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315c30(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315c64(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315e70(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315e80(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315eac(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_315f0c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_316354(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_31644c(uintptr_t);
extern uint32_t opencfw_em9305_phy_action_3164a8(uintptr_t);
const opencfw_em9305_phy_action_fn opencfw_em9305_slave_phy_actions_33565c[42]={
 opencfw_em9305_phy_action_315a28,0,opencfw_em9305_phy_action_315e70,0,0,opencfw_em9305_phy_action_31592c,0,
 opencfw_em9305_phy_action_316354,0,opencfw_em9305_phy_action_315e80,0,0,opencfw_em9305_phy_action_31592c,opencfw_em9305_phy_action_3164a8,
 opencfw_em9305_phy_action_316354,opencfw_em9305_phy_action_315eac,opencfw_em9305_phy_action_315e80,opencfw_em9305_phy_action_315f0c,opencfw_em9305_phy_action_315c30,opencfw_em9305_phy_action_31592c,0,
 opencfw_em9305_phy_action_316354,0,0,opencfw_em9305_phy_action_315f0c,0,0,opencfw_em9305_phy_action_31644c,
 opencfw_em9305_phy_action_316354,opencfw_em9305_phy_action_315eac,0,opencfw_em9305_phy_action_315f0c,0,0,0,
 opencfw_em9305_phy_action_316354,0,0,0,opencfw_em9305_phy_action_315c64,0,0,
};
const uint8_t opencfw_em9305_slave_phy_transitions_335704[42]={
 1u,0u,3u,0u,0u,1u,0u,
 1u,1u,3u,1u,1u,1u,2u,
 2u,5u,3u,0u,0u,2u,2u,
 3u,3u,3u,3u,3u,3u,4u,
 4u,5u,4u,4u,4u,4u,4u,
 5u,5u,5u,5u,0u,5u,5u,
};
_Static_assert(sizeof(opencfw_em9305_slave_phy_actions_33565c)==168u,"native slave table width");
