import React from 'react';
import './WaitingForOpponent.css'; 

export default function WaitingForOpponent() {
    return (
        <div className="waiting-for-opponent">
            <h2>Waiting for opponent's turn...</h2>
            <p>Please wait while the bot makes its move.</p>
        </div>
    );
}