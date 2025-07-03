import React from "react";
import "./Game.css";
import PublicView from "./PublicView";
import NamedPile from "./NamedPile";
import { SkipBoState } from "../gameLogic";

export default function Game() {
    const playerId = 0;
    const gameState: SkipBoState = {
        player_states: [
            {
                hand: [1, 2, 3, 0, 13],
                stock_pile: [4, 5, 6],
                discard_piles: [[7], [13], [13, 12, 12], [0]],
            },
            {
                hand: [8, 9, 10],
                stock_pile: [11],
                discard_piles: [[12], [7, 7, 7], [], []],
            },
        ],
        current_player: 0,
        build_piles: [[1, 2, 3, 4], [1, 13], [0], [1, 2, 3]],
        draw_pile: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        completed_build_piles: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        num_turns: 10,
        invalid_actions_count: 2,
        last_step: {
            action: {
                card_source: 1,
                card_destination: 2,
            },
            taken_by: playerId,
            was_valid: true,
        },
    };
    return (
        <div className="game">
            <h1>SkipBo Game</h1>
            <h3>Opponent</h3>
            <PublicView playerState={gameState.player_states[1]} />
            <NamedPile title="Build Piles" cards={gameState.build_piles} hideUnlessSkipbo={true} />
            <h3>You</h3>
            <PublicView playerState={gameState.player_states[playerId]} />
        </div>
    );
}