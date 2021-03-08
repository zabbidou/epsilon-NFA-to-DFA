import sys

# variabila pentru a memora inchiderile epsilon ale tuturor starilor
epsilon = []
# alfabetul NFA-ului
alphabet = set()
# helper pt redenumirea starilor DFA-ului
statesRename = {}
# helper pt redenumirea starilor DFA-ului
stateIndex = 0

class NFA:
    def __init__(self, l):
        # numarul de stari
        self.nrOfStates = int(l[0][0])
        # lista de stari finale
        self.final = [int(x) for x in l[1]]
        # tranzitiile
        self.trans = {}

        # luam fiecare lista si o impartim in stare, simbol, iar ce a ramas intra in lista next_states
        for state, symbol, *next_states in l[2:]:
            self.trans[(int(state), symbol)] = list(map(int, next_states))
            if symbol != "eps":
                alphabet.add(symbol)

    def __str__(self):
        return ("NFA:\nnr states: " + str(self.nrOfStates) + "\nfinal states: "
                 + str(self.final) + "\ntranzitii: " + str(self.trans))

class DFA:
    def __init__(self):
        # numarul de stari
        self.nrOfStates = 0
        # lista de stari finale
        self.final = []
        # tranzitiile
        self.trans = {}
        # helper pentru redenumire
        self.newTrans = {}

    def __str__(self):
        return ("DFA:\nnr states: " + str(self.nrOfStates) + "\nfinal states: "
                 + str(self.final) + "\ntranzitii: " + str(self.trans))

    # adaugarea unei tranzitii
    def addTransition(self, state, symbol, nextState):
        self.trans[(state, symbol)] = nextState

    # redenumirea starilor si completarea informatiilor despre DFA
    def finalTouches(self):
        self.nrOfStates = len(statesRename)
        # daca starea x a DFA-ului contine o stare a NFA-ului care e finala,
        # atunci si starea x este finala in DFA.
        for (state, key) in statesRename.items():
            for substate in state:
                if substate in nfa.final:
                    self.final.append(key)

        # redenumire
        for ((state, symbol), value) in self.trans.items():
            self.newTrans[(statesRename[state], symbol)] = statesRename[value]

        self.trans = self.newTrans

    # scrierea in fisier
    def printDFA(self):
        out = open(sys.argv[2], "w")
        print(self.nrOfStates, file = out)
        print(*self.final, file = out, sep = " ")
        
        for ((state, symbol), nextState) in self.trans.items():
            print(state, symbol, nextState, file = out)

# citirea din fisier
def readNFA(name):
    file = open(name, "r")
    l = list(map(lambda a: a.strip("\n").split(" "), file.readlines()))
    return l

def createNFA(l):
    return NFA(l)

# returneaza starile in care poti ajunge din starea "state" pe epsilon
def getEpsilonTrans(state):
    for (st, sym) in nfa.trans:
        if st == state and sym == "eps":
            return nfa.trans[(st, sym)]

    return []

# calculeaza inchiderea epsilon
def getEpsilonClosure(state):
    eps = {state}
    queue = []
    queue.extend(getEpsilonTrans(state))
    queue.append(state)
    eps.update(queue)

    while queue != []:
        currentState = queue.pop()
        queue += [x for x in getEpsilonTrans(currentState) if x not in eps]
        eps.update(queue)

    return eps

# calculeaza o stare a DFA-ului
def getDfaState(state, sym):
    newState = set()
    for st in state:
        if (st, sym) in nfa.trans:
            for nextState in nfa.trans[(st, sym)]:
                newState.update(epsilon[nextState])
            
    return tuple(newState)

# algoritmul principal de constructie
def constructDFA():
    global dfa
    global stateIndex
    global statesRename
    queue = []
    queue.append(epsilon[0])
    dfaStates = set()
    dfaStates.add(epsilon[0])
    statesRename[epsilon[0]] = stateIndex
    stateIndex += 1

    while queue != []:
        currentState = queue.pop()

        for sym in alphabet:
            newState = getDfaState(currentState, sym)
            dfa.addTransition(currentState, sym, newState)

            if newState not in dfaStates:
                dfaStates.add(newState)
                queue.append(newState)
                statesRename[newState] = stateIndex
                stateIndex += 1
    return dfa

if __name__ == "__main__":
    # citim si initializam
    nfa = NFA(readNFA(sys.argv[1]))
    dfa = DFA()

    print(nfa)

    # calculam inchiderile epsilon
    for i in range(nfa.nrOfStates):
        epsilon.append(tuple(getEpsilonClosure(i)))

    print(epsilon)

    # construim DFA-ul
    dfa = constructDFA()
    # formatarea output-ului
    dfa.finalTouches()

    #print(dfa.trans)

    # scrierea in fisier
    dfa.printDFA()
