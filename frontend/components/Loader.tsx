
import React, { useState, useEffect } from 'react';

const messages = [
    "Preparing audio for evaluation…",
    "Waiting for transcript and communication suggestions…",
    "Your video stays local for self-review."
];

const Loader: React.FC = () => {
    const [messageIndex, setMessageIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setMessageIndex(prevIndex => (prevIndex + 1) % messages.length);
        }, 2500);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="w-16 h-16 border-4 border-t-indigo-500 border-gray-600 rounded-full animate-spin mb-6"></div>
            <h2 className="text-2xl font-bold text-gray-200 mb-2">Aura is thinking...</h2>
            <p className="text-lg text-gray-400 transition-opacity duration-500">
                {messages[messageIndex]}
            </p>
        </div>
    );
};

export default Loader;
