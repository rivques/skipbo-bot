// CardRow.tsx
import React from "react";
import CardStack from "./CardStack";
import type { Card } from "./Game";

export default function CardRow({ cards, hideUnlessSkipbo }: { cards: Card[][]; hideUnlessSkipbo?: boolean }) {
    return (
        <div className="card-row">
            {cards.map((cardStack, index) => (
                <CardStack key={index} cards={cardStack} topDraggable={true} hideUnlessSkipbo={hideUnlessSkipbo} />
            ))}
        </div>
    );
}
