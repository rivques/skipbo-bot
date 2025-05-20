# skipbo-bot
Using reinforcement learning to play [Skip-Bo](https://en.wikipedia.org/wiki/Skip-Bo).


## Observations
An observation contains:
* The card on the agent's stock pile: `Discrete(14)`
* The number of cards left in the agent's stock pile: `Box(0,100,dtype=uint8)`
* The agent's current hand of up to 5 cards: `Tuple(Discrete(14),Discrete(14),Discrete(14),Discrete(14),Discrete(14))`
* The current value of each of the 4 build piles: `Tuple(Discrete(14),Discrete(14),Discrete(14),Discrete(14)`
* The size and top 3 values of each of the 4 discard piles: `Tuple(Dict({"top3": Tuple(Discrete(14),Discrete(14),Discrete(14)), "size": Box(0,100,dtype=uint8)}) * 4)`
* The card on the stock pile of the next player (NP): `Discrete(14)`
* The number of cards left in the NP's stock pile: `Box(0,100,dtype=uint8)`
* The top value in each of the NP's discard piles: `Tuple(Discrete(14),Discrete(14),Discrete(14),Discrete(14)`
```py
Dict({
    "stock": Discrete(14),
    "stock_size": Box(0, 100, dtype=uint8),
    "hand": Tuple(Discrete(14), Discrete(14), Discrete(14), Discrete(14), Discrete(14)),
    "build_piles": Tuple(Discrete(14), Discrete(14), Discrete(14), Discrete(14)),
    "discard_piles": Tuple(
        Dict({"top3": Tuple(Discrete(14), Discrete(14), Discrete(14)), "size": Box(0, 100, dtype=uint8)}),
        Dict({"top3": Tuple(Discrete(14), Discrete(14), Discrete(14)), "size": Box(0, 100, dtype=uint8)}),
        Dict({"top3": Tuple(Discrete(14), Discrete(14), Discrete(14)), "size": Box(0, 100, dtype=uint8)}),
        Dict({"top3": Tuple(Discrete(14), Discrete(14), Discrete(14)), "size": Box(0, 100, dtype=uint8)})
    ),
    "np_stock": Discrete(14),
    "np_stock_size": Box(0, 100, dtype=uint8),
    "np_discard_piles": Tuple(Discrete(14), Discrete(14), Discrete(14), Discrete(14)),
})
```

## Actions
Take the card in position [stock pile, hand 1-5, discard 1-4] and put it in [build pile 1-4, discard 1-4].
```py
Dict({"source": Discrete(10), "dest": Discrete(8)})
```
