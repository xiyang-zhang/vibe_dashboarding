# Local version control

The initial workspace contained Microsoft APM dependencies and a PBIX but no Git repository. Keep the original PBIX intact. Check status before changes and use a feature branch for substantial dashboard work. Stage reviewed source/config/docs/spec files and small deterministic fixtures; apm_modules is ignored and dependencies are reproduced via apm.yml/apm.lock.yaml. Commit changes with descriptive scopes (data/model/report/deneb). Never push remotely without approval.

Local caches, recovery files, credentials and machine-specific model_authoring_inputs.json are ignored. Change pMockDataRoot through the model parameter rather than committing another machine's absolute data directory. Do not silently change a live Desktop model's parameter or discard unsaved report state.
