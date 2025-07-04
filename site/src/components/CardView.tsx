// CardView.tsx
import React from "react";
import "./CardView.css";
import { Card } from "../gameLogic";

export default function CardView({ card, draggable, onDragStart }: { card: Card; draggable: boolean; onDragStart: (e: React.DragEvent) => void }) {
    if (card === 0) {
        return <div className="card empty"></div>;
    } else if (card === 13) {
        return (
            <div className="card skipbo" draggable={draggable} onDragStart={onDragStart}>
                <span className="card-corner card-corner-tl">SB</span>
                Skip<br />Bo
                <span className="card-corner card-corner-br">SB</span>
            </div>
        );
    } else {
        return (
            <div className={`card card-${card}`} draggable={draggable} onDragStart={onDragStart}>
                <span className="card-corner card-corner-tl">{card}</span>
                {card}
                <span className="card-corner card-corner-br">{card}</span>
            </div>
        );
    }
}
