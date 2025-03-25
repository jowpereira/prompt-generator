from typing import Dict, List, TypedDict, Optional, Literal, Any, Union

class UserRequirements(TypedDict, total=False):
    objetivo: str
    formato: Union[List[str], str]
    tom: Optional[str]
    restricoes: Optional[Dict[str, str]]
    exemplos: Optional[List[str]]
    
class PromptState(TypedDict, total=False):
    user_input: str
    requirements: UserRequirements
    draft_prompt: str
    formats: List[str]
    feedback: Optional[str]
    output: Optional[Dict[str, str]]
    error: Optional[str] 