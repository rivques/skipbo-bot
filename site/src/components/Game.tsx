import React from "react";
import "./Game.css";
import PublicView from "./PublicView";
import NamedPile from "./NamedPile";
// 0 means no card, 1-12 are the cards, 13 is the skipbo card
export type Card = number;

export interface PlayerState {
    /** up to 5 cards */
    hand: Card[];
    /** all the cards in the stock pile. index 0 is the bottom card */
    stock_pile: Card[];
    /** 4 discard piles. index 0 is the bottom card. Max 20. */
    discard_piles: Card[][];
}

export interface SkipBoAction {
    /** 0: stock pile, 1-5: hand, 6-9: discard piles */
    card_source: number;
    /** 0-3: build piles, 4-7: discard piles */
    card_destination: number;
}

export interface SkipBoLastStep {
    action: SkipBoAction;
    taken_by: number;
    was_valid: boolean;
}

export interface SkipBoState {
    player_states: PlayerState[];
    current_player: number;
    /** 4 build piles. index 0 is the bottom card */
    build_piles: Card[][];
    /** the deck of cards. index 0 is the bottom card */
    draw_pile: Card[];
    /** the completed build piles, together. */
    completed_build_piles: Card[];
    /** the number of turns taken so far */
    num_turns: number;
    /** the number of invalid actions taken in a row so far */
    invalid_actions_count: number;
    last_step?: SkipBoLastStep | null;
}

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
        current_player: playerId,
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