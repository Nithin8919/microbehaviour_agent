from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    behavior: str = Field(..., description="Atomic microbehavior description")
    explanation: Optional[str] = Field(None, description="Why this likely happens")
    nudge: Optional[str] = Field(None, description="Suggested intervention/UX change")
    priority: int = Field(5, ge=1, le=10)
    friction: Optional[str] = None
    frictionScore: Optional[int] = Field(None, ge=1, le=10)
    section: Optional[str] = Field(None, description="Page section association")


class TimelineStage(BaseModel):
    index: int
    stage: str
    section: Optional[str] = None
    observed: Optional[str] = None
    items: List[ExperienceItem] = Field(default_factory=list)


class ExperienceReport(BaseModel):
    url: str
    goal: Optional[str] = None
    items: List[ExperienceItem] = Field(default_factory=list)
    timeline: List[TimelineStage] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    url: str
    goal: Optional[str] = Field(None, description="Business goal, e.g., 'Book a call'")
    max_pages: int = Field(3, ge=1, le=15)
    max_depth: int = Field(1, ge=0, le=3)


class JourneyStep(BaseModel):
    step_number: int = Field(..., description="Sequential step number in the journey")
    step_name: str = Field(..., description="Name of the step (e.g., 'Land on homepage', 'Read headline')")
    description: str = Field(..., description="Detailed description of what happens in this step")
    content_elements: List[str] = Field(default_factory=list, description="Key content elements users interact with")
    user_actions: List[str] = Field(default_factory=list, description="Specific actions users take in this step")
    conversion_indicators: List[str] = Field(default_factory=list, description="Signs that users are progressing toward conversion")
    friction_points: List[str] = Field(default_factory=list, description="Potential obstacles or friction in this step")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Suggestions to optimize this step")
    microbehaviors: List[dict] = Field(default_factory=list, description="Microbehaviors associated with this step")


class UserJourneyReport(BaseModel):
    url: str = Field(..., description="URL of the analyzed website")
    journey_steps: List[JourneyStep] = Field(default_factory=list, description="Detailed breakdown of each journey step")
    total_steps: int = Field(..., description="Total number of steps in the journey")
    conversion_funnel_type: str = Field(..., description="Type of conversion funnel identified")
    primary_goal: str = Field(..., description="Primary conversion goal of the website")
    journey_complexity: str = Field(..., description="Complexity level of the user journey (Simple/Medium/Complex)")
    key_moments_of_truth: List[str] = Field(default_factory=list, description="Critical decision points in the journey")
    optimization_priorities: List[str] = Field(default_factory=list, description="Priority areas for optimization")


class ActionStep(BaseModel):
    step_number: int = Field(..., description="Sequential step number")
    action_type: str = Field(..., description="Type of action: view, read, click, fill, scroll, hover, submit, navigate")
    action_description: str = Field(..., description="Specific action description like 'Read headline: Transform Your Business'")
    content_target: str = Field(..., description="Exact content element being interacted with")
    friction_level: int = Field(1, ge=1, le=5, description="Friction level (1-5, where 5 is highest friction)")
    success_indicators: List[str] = Field(default_factory=list, description="Signs this step worked")
    failure_points: List[str] = Field(default_factory=list, description="What could go wrong")


class DropOffRisk(BaseModel):
    step_number: int = Field(..., description="Step number where drop-off risk occurs")
    risk_description: str = Field(..., description="Description of the drop-off risk")


class InteractionDetails(BaseModel):
    total_steps: int = Field(..., description="Total number of action steps")
    critical_path_steps: List[int] = Field(default_factory=list, description="Step numbers essential for conversion")
    optional_steps: List[int] = Field(default_factory=list, description="Step numbers that are nice to have but not required")
    drop_off_risks: List[DropOffRisk] = Field(default_factory=list, description="Potential drop-off points")
    optimization_sequence: List[str] = Field(default_factory=list, description="Step-by-step improvements")


class GranularActionReport(BaseModel):
    url: str = Field(..., description="URL of the analyzed website")
    goal: Optional[str] = Field(None, description="Business goal")
    action_sequence: List[ActionStep] = Field(default_factory=list, description="Granular step-by-step user actions")
    interaction_details: InteractionDetails = Field(..., description="Analysis of the interaction flow")


