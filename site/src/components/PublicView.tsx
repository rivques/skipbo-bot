// PublicView.tsx
import React from "react";
import NamedPile from "./NamedPile";
import { SkipBoState } from "../gameLogic";

export default function PublicView({ gameState, playerId, onDragOver, onDrop }: { gameState: SkipBoState, playerId: number, onDragOver: (e: React.DragEvent) => void; onDrop: (e: React.DragEvent) => void; }) {
    const playerState = gameState.player_states[playerId];
    const isThisPlayersTurn = gameState.current_player === playerId;
    return (
        <div className="public-view">
            <NamedPile title="Stock Pile" cards={[[playerState.stock_pile[playerState.stock_pile.length - 1]]]} sourceIds={isThisPlayersTurn ? [0] : [-1]} destIds={[-1]} onDragOver={onDragOver} onDrop={onDrop} />
            <NamedPile title="Discard Piles" cards={playerState.discard_piles.map(pile => pile.length === 0 ? [0] : pile)} sourceIds={isThisPlayersTurn ? [6, 7, 8, 9] : [-1, -1, -1, -1]} destIds={isThisPlayersTurn ? [4, 5, 6, 7] : [-1, -1, -1, -1]} onDragOver={onDragOver} onDrop={onDrop} />
        </div>
    );
}
