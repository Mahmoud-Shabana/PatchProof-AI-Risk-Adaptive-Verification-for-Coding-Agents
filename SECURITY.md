# Security Policy

PatchProof AI is a hackathon/research prototype that executes generated code only inside its controlled temporary workspace and requires explicit boundaries around file access.

## Reporting a security issue

Please do not publish credentials, API keys, private data, or exploit details in a public issue. Contact the repository owner, **Mahmoud Shabana**, through the GitHub profile at https://github.com/Mahmoud-Shabana.

## Scope notes

- Keep all credentials outside the repository.
- Treat model-generated patches as untrusted until tests and policy gates pass.
- Keep consequential actions sandboxed and require human approval before applying patches outside a test environment.
