"""
data/sample_data.py
-------------------
Default (sample) input so the app works immediately.

The whole problem is stored in ONE dictionary called `problem`:

    problem = {
        "days":               list of working day names,
        "num_periods":        periods per day,
        "classes":            {class name: number of students},
        "subjects":           [{"name", "teacher", "lectures"}, ...],
        "rooms":              {room name: capacity},
        "teacher_unavailable": [(teacher, day name, period number), ...],
    }

Simplification: every class studies every subject in the list.

NO FREE PERIOD: the lectures of one class must add up to (days x periods).
Here 6 subjects x 5 lectures = 30 = 5 days x 6 periods, so every slot is used.
"""

ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def get_sample_problem():
    """Return a ready-made problem (3 classes, 6 subjects, 5 teachers, 4 rooms)."""
    return {
        "days": ALL_DAYS[:5],          # Monday - Friday
        "num_periods": 6,              # 6 periods per day
        "classes": {
            "CE-A": 55,
            "CE-B": 48,
            "CE-C": 42,
        },
        "subjects": [
            {"name": "DBMS",  "teacher": "Prof. Sharma", "lectures": 5},
            {"name": "OS",    "teacher": "Prof. Verma",  "lectures": 5},
            {"name": "CN",    "teacher": "Prof. Iyer",   "lectures": 5},
            {"name": "AI",    "teacher": "Prof. Khan",   "lectures": 5},
            {"name": "Maths", "teacher": "Prof. Gupta",  "lectures": 5},
            {"name": "SE",    "teacher": "Prof. Gupta",  "lectures": 5},
        ],
        "rooms": {
            "R101": 60,
            "R102": 60,
            "R103": 50,
            "R104": 45,
        },
        # (teacher, day, period number starting from 1)
        "teacher_unavailable": [
            ("Prof. Verma", "Friday", 5),
            ("Prof. Verma", "Friday", 6),
            ("Prof. Khan", "Monday", 1),
        ],
    }
