// CardStack.tsx
import React from "react";
import CardView from "./CardView";
import { Card } from "../gameLogic";

export default function CardStack({ cards, topDraggable, hideUnlessSkipbo }: { cards: Card[]; topDraggable: boolean; hideUnlessSkipbo?: boolean }) {
    let displayCards = cards;
    if (hideUnlessSkipbo) {
        // Only show the top card, unless the top card is a skipbo (13),
        // in which case show all consecutive skipbos from the top
        let i = cards.length - 1;
        while (i > 0 && cards[i] === 13) {
            i--;
        }
        displayCards = cards.slice(i);
    }
    return (
        <div className="card-stack">
            {displayCards.map((card, index) => (
                <div key={index} className="card-stack-item">
                    <CardView card={card} draggable={index === displayCards.length - 1 && topDraggable} />
                </div>
            ))}
        </div>
    );
}
