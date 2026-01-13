export interface ModelResponse {
  model: string;
  response: string;
}

export interface RankingResponse {
  model: string;
  evaluation: string;
  ranking: string[];
}

export interface MessageMetadata {
  labelToModel: Record<string, string>;
  aggregateRankings: any[];
}

export interface Message {
  role: 'user' | 'assistant';
  content?: string;
  stage1?: ModelResponse[];
  stage2?: RankingResponse[];
  stage3?: string;
  metadata?: MessageMetadata;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  messages: Message[];
}

export interface AskResponse {
  conversation_id: string;
  stage1: ModelResponse[];
  stage2: RankingResponse[];
  stage3: string;
  metadata: MessageMetadata;
}
