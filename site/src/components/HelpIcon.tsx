// component that pops up a modal explaining how to play the game
import React from 'react';
import './HelpIcon.css';
export default function HelpIcon() {
    const [isOpen, setIsOpen] = React.useState(false);

    function toggleHelp() {
        setIsOpen(!isOpen);
    }

    return (
        <div className="help-icon">
            <div
                className="help-button"
                onClick={toggleHelp}
            >?</div>
            {isOpen && (
                <div className="help-modal" onClick={toggleHelp}>
                    <div className="help-content" onClick={(e) => e.stopPropagation()}>
                        <h2>What Is This?</h2>
                        <p>
                            This is a demo of a Skip-Bo-playing reinforcement learning agent I've trained. It's
                            not very good, but I learned a lot about reinforcement learning in the process.
                        </p>
                        <p>
                            This is also my first React project, which hopefully explains the... mediocre UI.
                        </p>
                        <h2>How Do I Play?</h2>
                        <p>
                            When it's your turn, drag and drop cards from your hand, stock pile, or discard piles
                            onto the build piles or your discard piles. Then wait for the bot to take its turn.
                        </p>
                        <h2>What are the rules of the game?</h2>
                        <p>
                            See <a href="https://officialgamerules.org/game-rules/skip-bo/#:~:text=Making%20a%20Play" target='_blank' rel="noreferrer">here</a>.
                        </p>
                        <h2>Where's the source code?</h2>
                        <p>
                            See <a href="https://github.com/rivques/skipbo-bot" target='_blank' rel="noreferrer">GitHub</a>.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}