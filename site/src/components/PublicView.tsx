// PublicView.tsx
import React from "react";
import NamedPile from "./NamedPile";
import { PlayerState } from "../gameLogic";

export default function PublicView({ playerState }: { playerState: PlayerState }) {
    return (
        <div className="public-view">
            <NamedPile title="Stock Pile" cards={[[playerState.stock_pile[playerState.stock_pile.length - 1]]]} />
            <NamedPile title="Discard Piles" cards={playerState.discard_piles} />
        </div>
    );
}
