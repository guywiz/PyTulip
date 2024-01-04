from ParticipationCoefficient import *

def test_plugin():
    G = tlp.newGraph()
    nodes = [G.addNode() for i in range(6)]
    G.addEdge(nodes[0], nodes[1])
    G.addEdge(nodes[0], nodes[2])
    G.addEdge(nodes[1], nodes[2])
    #
    G.addEdge(nodes[3], nodes[4])
    G.addEdge(nodes[3], nodes[5])
    G.addEdge(nodes[4], nodes[5])
    #
    G.addEdge(nodes[2], nodes[3])

    assert (G.numberOfNodes() == 6)

    community = G.getIntegerProperty('community')
    particip = G.getDoubleProperty('participation')
    params = tlp.getDefaultPluginParameters('Participation Coefficient', G)
    params['communities'] = community
    params['result'] = particip
    G.applyDoubleAlgorithm('Participation Coefficient', particip, params)

    assert (particip[nodes[0]] == 0.0)
    assert (particip[nodes[1]] == 0.0)
    assert (particip[nodes[4]] == 0.0)
    assert (particip[nodes[5]] == 0.0)
    
    assert (int(particip[nodes[2]] * 100)/100 == 0.44)
    assert (int(particip[nodes[3]] * 100)/100 == 0.44)
