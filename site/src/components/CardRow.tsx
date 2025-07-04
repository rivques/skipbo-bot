// CardRow.tsx
import React from "react";
import CardStack from "./CardStack";
import { Card } from "../gameLogic";

export default function CardRow({ cards, hideUnlessSkipbo, sourceIds, destIds, onDragOver, onDrop }: { cards: Card[][]; hideUnlessSkipbo?: boolean; sourceIds: number[]; destIds: number[]; onDragOver: (e: React.DragEvent) => void; onDrop: (e: React.DragEvent) => void; }) {
    return (
        <div className="card-row">
            {cards.map((cardStack, index) => (
                <CardStack key={index} cards={cardStack} hideUnlessSkipbo={hideUnlessSkipbo} sourceId={sourceIds[index]} destId={destIds[index]} onDragOver={onDragOver} onDrop={onDrop} />
            ))}
        </div>
    );
}
