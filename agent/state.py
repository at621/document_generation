from typing import TypedDict, List, Dict, Optional, Any


class TokenUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


class StyleGuide(TypedDict):
    overall_tone_and_style: str


class OutlineMetadata(TypedDict):
    version: str
    created_date: str
    author: str


class SourceHints(TypedDict):
    priority: str
    internal_files: List[str]
    public_references: List[str]


class ChapterWork(TypedDict):
    chapter_details: Dict
    research_results: Optional[str]
    generated_text: Optional[str]
    review_feedback: Optional[str]
    review_decision: Optional[str]
    token_usage: Dict[str, TokenUsage]


class GraphState(TypedDict):
    outline: Dict
    styleguide: StyleGuide
    metadata: OutlineMetadata
    chapters_to_process: List[Dict]
    chapter_works: Dict[str, ChapterWork]
    current_chapter_id: Optional[str]
    completed_chapters: Dict[str, Dict]
    final_document: Optional[str]
    total_token_usage: TokenUsage
    token_log: List[Dict]


# Subgraph-specific states
class ResearcherState(TypedDict):
    # Core state
    current_chapter_id: str
    chapter_works: Dict

    # Intermediate values (used between nodes)
    current_chapter: Optional[Dict]
    current_work: Optional[Dict]
    raw_search_results: Optional[Dict[str, str]]
    cached_web_results: Optional[Dict[str, List[Dict]]]

    # Final output
    research_results: Optional[str]

    # Configuration
    knowledge_base_path: Optional[str]
    knowledge_base_additional_path: Optional[str]
    embedding_model: Optional[str]

    # Token tracking
    total_tokens: Dict[str, Any]


class WriterState(TypedDict):
    current_chapter_id: str
    chapter_works: Dict[str, ChapterWork]
    styleguide: StyleGuide
    total_token_usage: TokenUsage
    token_log: List[Dict]


class ReviewerState(TypedDict):
    current_chapter_id: str
    chapter_works: Dict[str, ChapterWork]
    styleguide: StyleGuide
    total_token_usage: TokenUsage
    token_log: List[Dict]
