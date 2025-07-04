// CardStack.tsx
import React from "react";
import CardView from "./CardView";
import { Card } from "../gameLogic";

export default function CardStack({ cards, hideUnlessSkipbo, sourceId, destId, onDragOver, onDrop }: { cards: Card[]; hideUnlessSkipbo?: boolean; sourceId: number; destId: number; onDragOver: (e: React.DragEvent) => void; onDrop: (e: React.DragEvent) => void; }) {
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
    function handleCardDragStart(e: React.DragEvent, sourceId: number) {
        e.dataTransfer.clearData();
        e.dataTransfer.setData("text/plain", sourceId.toString());

    }
    return (
        <div className="card-stack" data-source-id={sourceId} data-dest-id={destId} onDragOver={onDragOver} onDrop={onDrop}>
            {displayCards.map((card, index) => (
                <div key={index} className="card-stack-item">
                    <CardView card={card} draggable={index === displayCards.length - 1 && sourceId > -1} onDragStart={(e) => handleCardDragStart(e, sourceId)} />
                </div>
            ))}
        </div>
    );
}
