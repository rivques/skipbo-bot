// NamedPile.tsx
import React from "react";
import CardRow from "./CardRow";
import type { Card } from "./Game";

export default function NamedPile({ title, cards, hideUnlessSkipbo }: { title: string; cards: Card[][]; hideUnlessSkipbo?: boolean }) {
    return (
        <div className="named-pile">
            <h3>{title}</h3>
            <CardRow cards={cards} hideUnlessSkipbo={hideUnlessSkipbo} />
        </div>
    );
}
