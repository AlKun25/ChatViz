// Global types and interfaces are stored here.
export interface Margin {
    readonly left: number;
    readonly right: number;
    readonly top: number;
    readonly bottom: number;
}

export interface ComponentSize {
    width: number;
    height: number;
}

export interface Point {
    readonly posX: number;
    readonly posY: number;
}

export interface Bar{
    readonly value: number;
}

export interface Messages {
    message_id: string;
    embedding: string;
    cluster: string;
    cluster_summary: string;
    content: string;
    openai_moderation: string;
    toxicity: string;
    role: string;
    turn: number;
    model: string;
}