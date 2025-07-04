import React from "react";
import "./Game.css";
import PublicView from "./PublicView";
import NamedPile from "./NamedPile";
import { createBaseState, isActionValid, SkipBoState, SkipBoAction, stepState, isGameOver } from "../gameLogic";
import { backOff } from "exponential-backoff";
import WaitingForOpponent from "./WaitingForOpponent";

async function getRemoteAction(state: SkipBoState, current_player: number): Promise<SkipBoAction | null> {
    // This function is a placeholder for any remote action logic.
    const response = await backOff(() => fetch("/get-move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            game_state: state,
            current_player: current_player
        })
    }));

    if (!response.ok) {
        console.error("Failed to fetch remote action:", response.statusText);
        return null;
    }

    const data = await response.json();
    if (data.action) {
        console.log("Remote action received:", data.action);
        return data.action as SkipBoAction;
    }
    return null;
}

export default function Game() {
    const [gameState, setGameState] = React.useState<SkipBoState>(createBaseState(2, 20));
    const [gettingRemoteAction, setGettingRemoteAction] = React.useState<boolean>(false);
    const myPlayerId = 0;

    function handleCardDragOver(e: React.DragEvent) {
        const sourceId = e.dataTransfer.getData("text/plain");
        const destId = e.currentTarget.getAttribute("data-dest-id") || "-1";
        console.log("Card dragged from:", sourceId, "to:", destId);
        const action: SkipBoAction = {
            card_source: parseInt(sourceId),
            card_destination: parseInt(destId)
        };
        if (isActionValid(gameState, action)) {
            e.preventDefault(); // Allow drop if the action is valid
        } else {
            console.log("Invalid action:", action);
        }
    }

    async function handleCardDrop(e: React.DragEvent) {
        e.preventDefault();
        const sourceId = e.dataTransfer.getData("text/plain");
        const destId = e.currentTarget.getAttribute("data-dest-id") || "-1";
        console.log("Card dropped from:", sourceId, "to:", destId);
        const action: SkipBoAction = {
            card_source: parseInt(sourceId),
            card_destination: parseInt(destId)
        };
        setGameState(stepState(gameState, action));

        if (isGameOver(gameState)) {
            alert(`Game over! You win!`);
            setGameState(createBaseState(2, 20)); // Reset the game state
        }
        setGettingRemoteAction(true);
        while (gameState.current_player !== myPlayerId) {
            console.log("Waiting for opponent's turn...");
            const remoteAction = await getRemoteAction(gameState, gameState.current_player);
            if (remoteAction) {
                await new Promise(resolve => setTimeout(resolve, 2000)); // Give the player a chance to see what's happened
                console.log("Remote action received:", remoteAction);
                setGameState(stepState(gameState, remoteAction));
                await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate waiting for the opponent's action

                if (isGameOver(gameState)) {
                    alert(`Game over! You lose!`);
                    setGameState(createBaseState(2, 20)); // Reset the game state
                    return;
                }
            }
        }
        setGettingRemoteAction(false);
    }

    let myView;
    if (gettingRemoteAction) {
        myView = <WaitingForOpponent />;
    } else {
        myView = (
            <>
                <h3>Your Board</h3>
                <div className="my-view">
                    <PublicView gameState={gameState} playerId={myPlayerId} onDragOver={handleCardDragOver} onDrop={handleCardDrop} />
                    <NamedPile title="Hand" cards={gameState.player_states[myPlayerId].hand.map(card => [card])} sourceIds={[1, 2, 3, 4, 5]} destIds={[-1, -1, -1, -1, -1]} onDragOver={handleCardDragOver} onDrop={handleCardDrop} />
                </div>
            </>
        );
    }

    return (
        <div className="game">
            <h1>ML SkipBo Bot</h1>
            <h2>by <a href="https://rivques.dev" target="_blank" rel="noreferrer">rivques</a>
            <br />
            for info, click the help icon</h2>
            <div className="game-state">
                <div className="column-left">
                    {myView}
                </div>
                <div className="column-center">
                    <h3>Current player: {gameState.current_player === 0 ? "You" : "Robot"}</h3>
                    <div className="build-piles">
                        <NamedPile title="Build Piles" cards={gameState.build_piles.map(pile => pile.length === 0 ? [0] : pile)} hideUnlessSkipbo={false} sourceIds={[-1, -1, -1, -1]} destIds={[0, 1, 2, 3]} onDragOver={handleCardDragOver} onDrop={handleCardDrop} />
                    </div>
                </div>
                <div className="column-right">
                    <h3>Robot's Board</h3>
                    <div className="opponent-view">
                        <PublicView gameState={gameState} playerId={1} onDragOver={handleCardDragOver} onDrop={handleCardDrop} />
                    </div>
                </div>
            </div>
        </div>
    );
}