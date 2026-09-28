# Back end: the API the front end calls.
# Every request goes through the guards first, then to a feature module.

# TODO: create the web API (e.g. FastAPI) with one endpoint per feature:
#   POST /qa                 -> features.qa_generator + features.interviewer_questions
#   POST /job-analysis       -> features.job_analyzer
#   POST /intro              -> features.intro_polisher
#   POST /resume-match       -> features.resume_matcher
