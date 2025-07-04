// NamedPile.tsx
import React from "react";
import CardRow from "./CardRow";
import { Card } from "../gameLogic";

export default function NamedPile({ title, cards, hideUnlessSkipbo, sourceIds, destIds, onDragOver, onDrop }: { title: string; cards: Card[][]; hideUnlessSkipbo?: boolean; sourceIds: number[]; destIds: number[]; onDragOver: (e: React.DragEvent) => void; onDrop: (e: React.DragEvent) => void; }) {
    return (
        <div className="named-pile">
            <h3>{title}</h3>
            <CardRow cards={cards} hideUnlessSkipbo={hideUnlessSkipbo} sourceIds={sourceIds} destIds={destIds} onDragOver={onDragOver} onDrop={onDrop} />
        </div>
    );
}
