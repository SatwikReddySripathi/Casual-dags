"""Edge schema for the Hattie-style variable subset DAG."""

DAG_EDGES = [
    ("prior_achievement", "student_confidence"),
    ("prior_achievement", "error_rate"),
    ("prior_achievement", "learning_outcome"),
    ("language_background", "student_confidence"),
    ("language_background", "error_rate"),
    ("engagement_history", "hint_dependency"),
    ("engagement_history", "learning_outcome"),
    ("teacher_clarity", "student_confidence"),
    ("teacher_clarity", "error_rate"),
    ("feedback_quality", "error_rate"),
    ("feedback_quality", "learning_outcome"),
    ("scaffolding", "hint_dependency"),
    ("scaffolding", "learning_outcome"),
    ("student_confidence", "learning_outcome"),
    ("error_rate", "learning_outcome"),
    ("hint_dependency", "learning_outcome"),
]
